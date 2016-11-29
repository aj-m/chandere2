"""Core module and entry point to Chandere2, which validates
command-line input and controls the asynchronous event loop.
"""

import asyncio
import signal
import sys

import aiohttp.errors

from chandere2.cli import PARSER
from chandere2.connection import (download_file, fetch_uri, try_connection,
                                  wrap_semaphore)
from chandere2.output import Console
from chandere2.post import (cache_posts, find_files, filter_posts,
                            get_threads, iterate_posts)
from chandere2.validate import (get_filters, get_path, get_targets)
from chandere2.write import (archive_plaintext, archive_sqlite, create_archive)

MAX_CONNECTIONS = 8


def main(parser=PARSER, output=None):
    """Command-line entry-point to Chandere2."""
    args = parser.parse_args()
    output = output or Console(debug=args.debug)

    target_uris, failed = get_targets(args.targets, args.imageboard, args.ssl)
    for pattern in failed:
        output.write_error("Invalid target \"%s\"" % pattern)
    if not target_uris:
        output.write_error("No valid targets provided.")
        sys.exit(1)

    path = get_path(args.output, args.mode, args.output_format)
    if path is None:
        output.write_error("The given output path cannot be written to.")
        sys.exit(1)

    filters, failed = get_filters(args.filters, args.imageboard)
    for argument in failed:
        output.write_error("Invalid filter pattern \"%s\"" % argument)

    create_archive(args.mode, args.output_format, path)

    try:
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, clean_up)
        if args.mode is None:
            target_operation = try_connection(target_uris, output)
            loop.run_until_complete(target_operation)
        else:
            target_operation = main_loop(target_uris, path, filters,
                                         args, output)
            loop.run_until_complete(target_operation)
    finally:
        loop.close()


def clean_up():
    """Safe clean up function to cancel pending tasks."""
    for task in asyncio.Task.all_tasks():
        task.cancel()


def get_operations(target_uris: dict, cap_connections: bool) -> list:
    """Creates a list of coroutines for connecting to each of the
    targets, and will wrap their execution into a semaphore if
    cap_connections is True.
    """
    operations = []
    if cap_connections:
        connection_cap = asyncio.Semaphore(MAX_CONNECTIONS)
        for uri in target_uris:
            last_load = target_uris[uri][2]
            target_operation = fetch_uri(uri, last_load)
            wrapped = wrap_semaphore(target_operation, connection_cap)
            operations.append(wrapped)
    else:
        for uri in target_uris:
            last_load = target_uris[uri][2]
            target_operation = fetch_uri(uri, last_load)
            operations.append(target_operation)
    return operations


async def handle_file(filename: str, image: str, path: str, ssl: bool, output):
    """Coroutine to handle file downloading."""
    image = "https://" + image if ssl else "http://" + image
    output.write_debug("File %s found at %s." % (filename, image))
    output.write("Downloading \"%s\"..." % filename)
    if await download_file(image, path, filename):
        output.write("Downloaded %s." % filename)
    else:
        output.write_error("Could not download %s." % filename)


async def main_loop(target_uris: dict, path: str, filters: list, args, output):
    """Loop to make sure targets get handled. Calls upon other
    coroutines to handle them as they are connected to, as well as
    deciding whether or not the program has finished.
    """
    cache = []
    iteration = 0
    imageboard = args.imageboard

    output.write_debug("Entering the main loop.")
    while True:
        iteration += 1
        operations = get_operations(target_uris, args.cap_connections)
        output.write_debug("Starting iteration %d." % iteration)

        for future in asyncio.as_completed(operations):
            try:
                content, error, last_load, uri = await future
            except aiohttp.errors.ClientOSError:
                output.write_error("Exception caught. The imageboard may "
                                   "require an SSL connection - run Chandere2 "
                                   "with the '--ssl' flag.")
                del target_uris[uri]
                continue
            except OSError:
                output.write_error("Exception caught. Are you sure you have a "
                                   "working internet connection right now? If "
                                   "so, check to see if the Imageboard is "
                                   "online.")
                del target_uris[uri]
                continue
            if error == 404:
                output.write_error("%s does not exist." % uri)
                del target_uris[uri]
                continue
            elif error:
                output.write_error("Could not connect to imageboard.")
                del target_uris[uri]
                continue

            board, thread, _ = target_uris[uri]
            output.write_debug("Connection made to %s..." % uri)

            if not thread:
                for uri in get_threads(content, board, imageboard):
                    target_uris[uri] = [board, True, ""]
            else:
                posts = iterate_posts(content, imageboard)
                posts = filter_posts(posts, filters)
                posts = cache_posts(posts, cache, imageboard)
                if args.mode == "fd":
                    for image, name in find_files(posts, board, imageboard):
                        await handle_file(name, image, path, args.ssl, output)
                elif args.mode == "ar":
                    output.write("Archiving %s..." % uri)
                    if args.output_format == "sqlite":
                        archive_sqlite(posts, path, board, imageboard)
                    else:
                        archive_plaintext(posts, path, imageboard)
                    output.write("Archiving successful.")

            target_uris[uri][2] = last_load

        if args.continuous:
            pass
        elif all(thread for _, thread, _ in target_uris.values()):
            break
        elif iteration > 1:
            break

"""Module for creating and handling URN's for an imageboard."""

import re
import urllib.parse

from chandere2.context import CONTEXTS


def generate_uri(board: str, thread: str, imageboard="4chan") -> str:
    """Forms a valid URN for the given board, thread and imageboard.
    None is returned if the imageboard does not have a known URI.
    """
    if imageboard in CONTEXTS:
        imageboard_uri = CONTEXTS.get(imageboard).get("uri")
    else:
        imageboard_uri = None

    if imageboard_uri is None:
        uri = None
    else:
        uri = "/".join((imageboard_uri, board, thread + ".json"))

    return uri


def strip_target(target: str) -> tuple:
    """Strips the given target string for a board initial and, if found,
    a thread number. A tuple containing the two will be returned, with 
    None as the thread if a thread number was not in the target string.
    """
    # The target should be quoted and stripped prior to further
    # handing, as Python has difficulty with some Unicode.
    target = urllib.parse.quote(target, safe="/ ", errors="ignore").strip()

    # The regular expression pattern matches a sequence of
    # characters not containing whitespace or a forward slash,
    # optionally preceded and succeeded by a forward slash.
    match = re.search(r"(?<=\/)?[^\s\/]+(?=[\/ ])?", target)
    board = match.group() if match else None

    # The regular expression pattern matches a sequence of digits
    # preceded by something that might look like a board and a
    # forward slash or space character, optionally succeeded by a
    # forward slash.
    match = re.search(r"(?<=[^\s\/][\/ ])\d+(?=\/)?", target)
    thread = match.group() if match else "threads"

    return (board, thread)

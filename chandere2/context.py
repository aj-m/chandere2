"""General information specific to certain imageboards."""

LYNXCHAN_IMAGE_FIELDS = ("originalName", "path", None, "files")
LYNXCHAN_POST_FIELDS = ("threadId", "creation", "name", "id", "subject",
                        "markdown", "originalName", None)

NEXT_IMAGE_FIELDS = ("filename", "file_id", None, "attachments")
NEXT_POST_FIELDS = ("board_id", "created_at", "author", "author_id", "subject",
                    "content_html", "filename", None)

VICHAN_IMAGE_FIELDS = ("filename", "tim", "ext", "extra_files")
VICHAN_POST_FIELDS = ("no", "time", "name", "trip",
                      "sub", "com", "filename", "ext")

CONTEXTS = {
    "4chan": {"uri": "a.4cdn.org",
              "threads_endpoint": "threads.json",
              "image_uri": "i.4cdn.org",
              "image_dir": None,
              "board_in_image_uri": True,
              "delimiter": "thread",
              "image_fields": VICHAN_IMAGE_FIELDS,
              "post_fields": VICHAN_POST_FIELDS,
              "reply_field": None,
              "image_pivot": None},
    "8chan": {"uri": "8ch.net",
              "threads_endpoint": "threads.json",
              "image_uri": "media.8ch.net",
              "image_dir": "src",
              "board_in_image_uri": True,
              "delimiter": "res",
              "image_fields": VICHAN_IMAGE_FIELDS,
              "post_fields": VICHAN_POST_FIELDS,
              "reply_field": None,
              "image_pivot": None},
    "76chan": {"uri": "76chan.org",
               "threads_endpoint": "threads.json",
               "image_uri": "76chan.org",
               "image_dir": "src",
               "board_in_image_uri": True,
               "delimiter": "res",
               "image_fields": VICHAN_IMAGE_FIELDS,
               "post_fields": VICHAN_POST_FIELDS,
               "reply_field": None,
               "image_pivot": None},
    "endchan": {"uri": "endchan.xyz",
                "threads_endpoint": "catalog.json",
                "image_uri": "endchan.xyz",
                "image_dir": None,
                "board_in_image_uri": False,
                "delimiter": "res",
                "image_fields": LYNXCHAN_IMAGE_FIELDS,
                "post_fields": LYNXCHAN_POST_FIELDS,
                "reply_field": "posts",
                "image_pivot": None},
    "lainchan": {"uri": "lainchan.org",
                 "threads_endpoint": "threads.json",
                 "image_uri": "lainchan.org",
                 "image_dir": "src",
                 "board_in_image_uri": True,
                 "delimiter": "res",
                 "image_fields": VICHAN_IMAGE_FIELDS,
                 "post_fields": VICHAN_POST_FIELDS,
                 "reply_field": None,
                 "image_pivot": None},
    "nextchan": {"uri": "nextchan.org",
                 "threads_endpoint": "catalog.json",
                 "image_uri": "nextchan.org",
                 "image_dir": "file",
                 "board_in_image_uri": True,
                 "delimiter": "thread",
                 "image_fields": NEXT_IMAGE_FIELDS,
                 "post_fields": NEXT_POST_FIELDS,
                 "reply_field": "replies",
                 "image_pivot": "pivot"}
}

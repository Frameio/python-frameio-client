### Asset Fields ###

asset_excludes = {
    "only_fields": [
        # "a.downloads",
        "a.name",
        "a.filesize",
        "u.name",
        "a.is_session_watermarked",
        "a.item_count",
        "a.creator.name" "a.creator.id",
        "a.inserted_at",
        "a.original",
        "a.upload_completed_at",
    ],
    "excluded_fields": ["a.checksums", "a.h264_1080_best", "a.source"],
    "drop_includes": ["a.trancode_statuses", "a.transcodes", "a.source", "a.checksums"],
    "hard_drop_fields": ["a.transcodes", "a.source"],
}

default_thread_count = 5

retryable_statuses = [400, 429, 500, 502, 503]
retryable_methods = ['GET', 'PUT', 'POST', 'DELETE']

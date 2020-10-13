import pytest
from frameioclient import FrameioClient


regular_asset = {
    "is_hls_required": False,
    "is_session_watermarked": False,
    "downloads": {
        "h264_720": "some-s3-url",
        "h264_1080_best": "some-other-s3-url"
    },
    "h264_720": "some-s3-url",
    "h264_1080_best": "some-other-s3-url"
    "original": "some-s3-url",
    "hls_manifest": "hls-url"
}

watermarked_asset_download_allowed: {
    "is_hls_required": True,
    "is_session_watermarked": True,
    "downloads": {
        "h264_720": "download-stream-service-url",
        "h264_1080_best": "download-stream-service-url"
    },
    "hls_manifest": "hls-url"
}

watermarked_asset_no_download = {
    "is_hls_required": True,
    "is_session_watermarked": True,
    "hls_manifest": "hls-url"
}

no_download_allowed = {
    "is_hls_required": True,
    "is_session_watermarked": False,
    "hls_manifest": "hls-url"
}

def test_FrameioClient(frameioclient):
  assert type(frameioclient) == FrameioClient

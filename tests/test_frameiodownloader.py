import pytest
from frameioclient import FrameioDownloader, DownloadException


regular_asset = {
    "is_hls_required": False,
    "is_session_watermarked": False,
    "downloads": {
        "h264_720": "some-720-url",
        "h264_1080_best": "some-1080-url"
    },
    "h264_720": "some-720-url",
    "h264_1080_best": "some-1080-url",
    "original": "some-original-url",
    "hls_manifest": "some-hls-url"
}

watermarked_asset_download_allowed = {
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

def test_get_download_key_returns_original():
    url = FrameioDownloader(regular_asset, './').get_download_key()
    assert url == regular_asset['original']

def test_get_download_key_returns_watermarked_download():
    url = FrameioDownloader(watermarked_asset_download_allowed, './').get_download_key()
    assert url == watermarked_asset_download_allowed['downloads']['h264_1080_best']

def test_get_download_key_fails_gracefully_on_watermarked_asset():
    with pytest.raises(DownloadException):
        FrameioDownloader(watermarked_asset_no_download, './').get_download_key()

def test_get_download_key_fails_gracefully_when_downloads_disallowed():
    with pytest.raises(DownloadException):
        FrameioDownloader(no_download_allowed, './').get_download_key()


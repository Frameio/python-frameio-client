import os
import sys

from utils import timefunc
import frameioclient

from frameioclient.lib.bandwidth import NetworkBandwidth


def download(
    asset_id: str = "",
    destination: str = "downloads",
    clean_up: bool = True,
    size: str = "small",
):
    token = os.getenv("FRAMEIO_TOKEN")
    client = frameioclient.FrameioClient(token)
    asset_info = client.assets.get(asset_id)
    download_info = client.assets.download(
        asset_info, destination, multi_part=True, replace=True
    )

    if clean_up == True:
        os.remove(download_info["destination"])

    return download_info


def test_s3():
    asset_list = []
    stats = []
    for asset in asset_list:
        report = download(asset_id=asset)
        stats.append(report)

    return stats


def test_cloudfront():
    asset_list = [
        "811baf7a-3248-4c7c-9d94-cc1c6c496a76",
        "35f8ac33-a710-440e-8dcc-f98cfd90e0e5",
        "e981f087-edbb-448d-baad-c8363b78f5ae",
    ]
    stats = []
    for asset in asset_list:
        report = download(asset_id=asset)
        stats.append(report)

    return stats


def build_metric(s3_stats, cf_stats, baseline):
    # Compare S3 against the baseline after calculating the average of the runs
    # Compare CF against the baseline after calculating the average of the runs
    # Compare S3 against CF and produce a number in Mbit/s {:.2j}?
    # Report the asset_id as well
    # Report whether something was a HIT or a MISS in cache
    # Report which CDN we hit
    print("Thing")
    pass


def run_benchmark():
    s3_stats = test_s3()
    cf_stats = test_cloudfront()
    # build_metrics(s3_stats, cf_stats, NetworkBandwidth)

    # ComparisonTest(self.user_id, transfer_stats, self.request_logs)


if __name__ == "__main__":
    # Old Method:
    # timefunc(benchmark_download, asset_id='811baf7a-3248-4c7c-9d94-cc1c6c496a76', destination='downloads', iterations=3) # large
    # timefunc(benchmark_download, asset_id='35f8ac33-a710-440e-8dcc-f98cfd90e0e5', destination='downloads', iterations=1) # medium
    # timefunc(benchmark_download, asset_id='e981f087-edbb-448d-baad-c8363b78f5ae', destination='downloads', iterations=5) # small

    # New method:
    run_benchmark()

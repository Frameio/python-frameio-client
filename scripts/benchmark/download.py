import os
import sys

from utils import timefunc
from frameioclient import FrameioClient


def benchmark_download(asset_id='', destination='', clean_up=True, size='small'):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    asset_info = client.assets.get(asset_id)
    accelerated_filename = client.assets.download(asset_info, destination, multi_part=True, concurrency=10)

    if clean_up == True:
        os.remove(accelerated_filename)

    return True

if __name__ == "__main__":    
    # timefunc(benchmark_download, asset_id='811baf7a-3248-4c7c-9d94-cc1c6c496a76', destination='./downloads', iterations=3) # large
    timefunc(benchmark_download, asset_id='35f8ac33-a710-440e-8dcc-f98cfd90e0e5', destination='./downloads', iterations=1) # medium
    # timefunc(benchmark_download, asset_id='e981f087-edbb-448d-baad-c8363b78f5ae', destination='./downloads', iterations=1) # small
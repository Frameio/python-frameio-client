import os
import sys

from utils import timefunc
from frameioclient import FrameioClient


def benchmark_upload(source_file='', remote_destination=''):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    client.assets.upload(remote_destination, source_file)

    return True

if __name__ == "__main__":    
    timefunc(benchmark_upload, source_file='', remote_destination='dd8526ee-2c7d-4b48-9bf7-b847664666bb', iterations=1) # medium

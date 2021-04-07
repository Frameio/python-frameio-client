import os
import sys
from timeit import default_timer as timer
from frameioclient import FrameioClient

from dataclasses import dataclass

@dataclass
class Asset:
    """Class for representing an Asset."""
    name: str
    id: uuid


def benchmark(asset_id='', destination='', clean_up=True, size='small'):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    asset_info = client.assets.get(asset_id)
    accelerated_filename = client.assets.download(asset_info, destination, multi_part=True, concurrency=10)

    if clean_up == True:
        os.remove(accelerated_filename)

    return True


def timefunc(func, *args, **kwargs):
    """Time a function. 

    args:
        iterations=3

    Usage example:
        timeit(myfunc, 1, b=2)
    """
    try:
        iterations = kwargs.pop('iterations')
    except KeyError:
        iterations = 3
    elapsed = sys.maxsize
    for _ in range(iterations):
        start = timer()
        result = func(*args, **kwargs)
        elapsed = min(timer() - start, elapsed)
    print(('Best of {} {}(): {:.9f}'.format(iterations, func.__name__, elapsed)))
    return result



if __name__ == "__main__":    
    # timefunc(benchmark, asset_id='811baf7a-3248-4c7c-9d94-cc1c6c496a76', destination='./downloads', iterations=3) # large
    timefunc(benchmark, asset_id='35f8ac33-a710-440e-8dcc-f98cfd90e0e5', destination='./downloads', iterations=1) # medium
    # timefunc(benchmark, asset_id='e981f087-edbb-448d-baad-c8363b78f5ae', destination='./downloads', iterations=1) # small
import os
import sys
from timeit import default_timer as timer
from frameioclient import FrameioClient

def benchmark(asset_id='', destination='', clean_up=True):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    asset_info = client.assets.get(asset_id)
    accelerated_filename = client.assets.download(asset_info, destination, multi_part=True, concurrency=10)

    if clean_up == True:
        os.remove(os.path.join(destination, asset_info['name']))

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
    timefunc(benchmark, asset_id='811baf7a-3248-4c7c-9d94-cc1c6c496a76', destination='/Volumes/Jeff-EXT/Python Transfer Test', iterations=3)
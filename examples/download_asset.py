import os
from frameioclient import FrameioClient

def benchmark(asset_id):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    asset_info = client.assets.get(asset_id)
    accelerated_filename = client.download(asset_info, "downloads", prefix="accelerated_", multi_part=True, concurrency=20)

    # print("Normal speed: {}, Accelerated speed: {}".format(normal_speed, accelerated_speed))

if __name__ == "__main__":
    # download_file("60ff4cca-f97b-4311-be24-0eecd6970c01")
    benchmark("20a1df34-e8ad-48fd-b455-c68294cc7f71")
    # benchmark("9cee7966-7db1-4066-b326-f9e6f5e929e4")
import os

from frameioclient import FrameioClient

def benchmark(asset_id):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    asset_info = client.get_asset(asset_id)
    normal_filename, normal_speed = client.download(asset_info, "downloads", prefix="normal_", acceleration_override=False)
    accelerated_filename, accelerated_speed = client.download(asset_info, "downloads", prefix="accelerated_", acceleration_override=True)

    # normal = client.download(asset_info, "downloads", prefix="normal_", acceleration_override=False)
    # accelerated = client.download(asset_info, "downloads", prefix="accelerated_", acceleration_override=True)

    # print(normal, accelerated)

    print("Normal speed: {}, Accelerated speed: {}".format(normal_speed, accelerated_speed))

if __name__ == "__main__":
    # download_file("60ff4cca-f97b-4311-be24-0eecd6970c01")
    benchmark("811baf7a-3248-4c7c-9d94-cc1c6c496a76")
    # benchmark("9cee7966-7db1-4066-b326-f9e6f5e929e4")

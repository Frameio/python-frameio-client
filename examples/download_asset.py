import os

from frameioclient import FrameioClient

def download_file(asset_id):
    token = os.getenv("FRAMEIO_TOKEN")
    client = FrameioClient(token)
    asset_info = client.get_asset(asset_id)
    client.download(asset_info, "downloads")

if __name__ == "__main__":
    download_file("6cc9a45f-64a7-456e-a95f-98687220bf6e")
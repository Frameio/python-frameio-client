import os
from frameioclient import FrameioClient


token = os.getenv('FRAMEIO_TOKEN')

def create_comments(asset_id: str, count=7449) -> bool:
    client = FrameioClient(token)

    try:
        for i in range(count):
            client.comments.create(asset_id=asset_id, text="Test comment")

        return True
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    asset_id = "5efaf3c3-e0fe-4742-bce1-1ce57f87c4bb"
    create_comments(asset_id)

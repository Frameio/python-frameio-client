import os
from frameioclient import FrameioClient

def leave_range_based_comment(asset_id, comment):
    client = FrameioClient(os.getenv("FRAME_IO_TOKEN"))
    res = client.comments.create(
        asset_id=asset_id,
        text="This is my range based comment",
        timestamp=1911,
        duration=3.5
    )

    print(res)


if __name__ == "__main__":
    leave_range_based_comment("id", "this is my comment!")
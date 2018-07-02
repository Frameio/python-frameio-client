from frameioclient import FrameioClient
import os

def main():
  client = FrameioClient("TOKEN")

  filesize = os.path.getsize('demo.mov')

  asset = client.create_asset(
    parent_asset_id="PARENT_ASSET_ID",
    name="Test123.mov",
    type="file",
    filetype="video/quicktime",
    filesize=filesize
  )

  file = open('demo.mov')
  client.upload(asset, file)

if __name__ == "__main__":
  main()

from frameioclient import FrameioClient
import mimetypes
import os

def main():
  client = FrameioClient("TOKEN")

  filesize = os.path.getsize('demo.mov')

  asset = client.create_asset(
    parent_asset_id="PARENT_ASSET_ID",
    name="Test123.mov",
    type="file",
    filetype=mimetypes.read_mime_types("demo.mov"),
    filesize=filesize
  )

  file = open("demo.mov", "rb")
  client.upload(asset, file)

if __name__ == "__main__":
  main()

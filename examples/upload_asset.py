from frameioclient import FrameioClient

def main():
  client = FrameioClient("TOKEN")
  file_path = './file_to_upload.mov'
  parent_asset_id = ''

  asset = client.assets.upload(parent_asset_id,file_path)

if __name__ == "__main__":
  main()

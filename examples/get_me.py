from frameioclient import FrameioClient
import os

def main():
  TOKEN = os.getenv("FRAME_IO_TOKEN")
  client = FrameioClient(TOKEN)
  me = client.get_me()
  print(me['id'])

if __name__ == "__main__":
  main()

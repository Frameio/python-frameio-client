from frameioclient import FrameioClient

def main():
  client = FrameioClient("TOKEN")
  me = client.get_me()
  print(me['id'])

if __name__ == "__main__":
  main()

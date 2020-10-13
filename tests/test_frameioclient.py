from frameioclient import FrameioClient

def test_FrameioClient(setup_client):
  client = setup_client
  assert type(client) == FrameioClient 
import pytest
import os

from frameioclient import FrameioClient

token = os.getenv('FRAME_IO_TOKEN')

@pytest.fixture()
def setup_client():
  client = FrameioClient(token)
  return client
  
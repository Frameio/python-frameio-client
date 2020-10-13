import os
import pytest
from frameioclient import FrameioClient


@pytest.fixture
def frameioclient(token):
  return FrameioClient("aaaabbbbccccddddeeee")

token = os.getenv('FRAME_IO_TOKEN')

@pytest.fixture()
def setup_client():
  client = FrameioClient(token)
  return client

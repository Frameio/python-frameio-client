import os
import pytest
from frameioclient import FrameioClient

token = os.getenv('FRAME_IO_TOKEN')

# @pytest.fixture
# def frameioclient(token):
#   return FrameioClient("aaaabbbbccccddddeeee")


@pytest.fixture()
def setup_client():
  client = FrameioClient(token)
  return client

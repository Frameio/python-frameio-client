import pytest
from frameioclient import FrameioClient

@pytest.fixture
def frameioclient(token):
  return FrameioClient("aaaabbbbccccddddeeee")

import pytest
from frameioclient import FrameioClient

def test_FrameioClient(frameioclient):
  assert type(frameioclient) == FrameioClient

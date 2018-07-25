# python-frameio-client

Official Python client for the Frame.io API.

## Overview

### Installation

via Pip
```
$ pip install frameioclient
```

via Source
```
$ git clone https://github.com/frameio/python-frameio-client
$ pip install .
```

## Documentation

[Frame.io API Documentation](https://docs.frame.io)

## Usage

_Note: A valid token is required to make requests to Frame.io. Please contact platform@frame.io to get setup._

In addition to the snippets below, examples are included in [/examples](/examples).

### Get User Info

Get basic info on the authenticated user.

```python
from frameioclient import FrameioClient

client = FrameioClient("TOKEN")
me = client.get_me()
print(me['id'])
```

### Create and Upload Asset

Create a new asset and upload a file. For more information on how assets work, check out [our docs](https://docs.frame.io).

```python
from frameioclient import FrameioClient
import os

client = FrameioClient("TOKEN")

filesize = os.path.getsize("sample.mp4")

# Create a new asset.
asset = client.create_asset(
  parent_asset_id="1234abcd",
  name="MyVideo.mp4",
  type="file",
  filetype="video/mp4",
  filesize=filesize
)

# Upload the file at the target asset.
file = open("sample.mp4", "rb")
client.upload(asset, file)
```

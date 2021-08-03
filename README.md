# python-frameio-client

[![PyPI version](https://badge.fury.io/py/frameioclient.svg)](https://badge.fury.io/py/frameioclient)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/frameioclient.svg)](https://pypi.python.org/pypi/frameioclient/)


<img width="1644" alt="artboard_small" src="https://user-images.githubusercontent.com/19295862/66240171-ba8dd280-e6b0-11e9-9ccf-573a4fc5961f.png">

# Frame.io 
Frame.io is a cloud-based collaboration hub that allows video professionals to share files, comment on clips real-time, and compare different versions and edits of a clip. 

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

### Developing
Install the package into your development environment and link to it by running the following:

```sh
pipenv install -e . -pre
```

## Documentation

[Frame.io API Documentation](https://developer.frame.io/docs)

### Use CLI
When you install this package, a cli tool called `fioctl` will also be installed to your environment.

**To upload a file or folder**
```sh
fioctl \
--token fio-u-YOUR_TOKEN_HERE  \
--destination "YOUR TARGET FRAME.IO PROJECT OR FOLDER" \
--target "YOUR LOCAL SYSTEM DIRECTORY" \
--threads 8
```

**To download a file, project, or folder**
```sh
fioctl \
--token fio-u-YOUR_TOKEN_HERE  \
--destination "YOUR LOCAL SYSTEM DIRECTORY" \
--target "YOUR TARGET FRAME.IO PROJECT OR FOLDER" \
--threads 2
```

### Links

**Sphinx Documentation**
- https://pythonhosted.org/sphinxcontrib-restbuilder/
- https://www.npmjs.com/package/rst-selector-parser
- https://sphinx-themes.org/sample-sites/furo/_sources/index.rst.txt
- https://developer.mantidproject.org/Standards/DocumentationGuideForDevs.html
- https://sublime-and-sphinx-guide.readthedocs.io/en/latest/code_blocks.html
- https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
- https://stackoverflow.com/questions/64451966/python-sphinx-how-to-embed-code-into-a-docstring
- https://pythonhosted.org/an_example_pypi_project/sphinx.html

**Decorators**
- https://docs.python.org/3.7/library/functools.html
- https://realpython.com/primer-on-python-decorators/
- https://www.sphinx-doc.org/en/master/usage/quickstart.html
- https://www.geeksforgeeks.org/decorators-with-parameters-in-python/
- https://stackoverflow.com/questions/43544954/why-does-sphinx-autodoc-output-a-decorators-docstring-when-there-are-two-decora


## Usage

_Note: A valid token is required to make requests to Frame.io. Go to our [Developer Portal](https://developer.frame.io/) to get a token!_

In addition to the snippets below, examples are included in [/examples](/examples).

### Get User Info

Get basic info on the authenticated user.

```python
from frameioclient import FrameioClient

client = FrameioClient("TOKEN")
me = client.users.get_me()
print(me['id'])
```

### Create and Upload Asset

Create a new asset and upload a file. For `parent_asset_id` you must have the root asset ID for the project, or an ID for a folder in the project. For more information on how assets work, check out [our docs](https://developer.frame.io/docs/workflows-assets/uploading-assets).

```python
import os
from frameioclient import FrameioClient

client = FrameioClient("TOKEN")


# Create a new asset manually
asset = client.assets.create(
  parent_asset_id="1234abcd",
  name="MyVideo.mp4",
  type="file",
  filetype="video/mp4",
  filesize=os.path.getsize("sample.mp4")
)

# Create a new folder
client.assets.create(
  parent_asset_id="",
  name="Folder name",
  type="folder" # this kwarg is what makes it a folder
)

# Upload a file 
client.assets.upload(destination_id, "video.mp4")
```

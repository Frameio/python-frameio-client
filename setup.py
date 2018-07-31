import setuptools

with open("README.md", "r") as f:
  long_description = f.read()

setuptools.setup(
  name='frameioclient',
  version='0.3.1',
  description='Client library for the Frame.io API',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/frameio/python-frameio-client',
  packages=setuptools.find_packages(),
  author='Frame.io, Inc.',
  author_email='platform@frame.io',
  license='MIT'
)

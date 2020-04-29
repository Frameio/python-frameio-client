import sys
import os
import setuptools

from setuptools.command.install import install

version='0.7.5'

with open("README.md", "r") as f:
  long_description = f.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != version:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, version
            )
            sys.exit(info)

setuptools.setup(
  name='frameioclient',
  version=version,
  python_requires='>=2.7.17, !=3.6.*, <4',
  install_requires=[
    'requests',
    'urllib3',
    'importlib-metadata ~= 1.0 ; python_version < "3.8"',
  ],
  extras_require={
    'dev': [
      'bump2version',
    ]
  },
  description='Client library for the Frame.io API',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/frameio/python-frameio-client',
  packages=setuptools.find_packages(),
  author='Frame.io, Inc.',
  author_email='platform@frame.io',
  license='MIT',
  cmdclass={
    'verify': VerifyVersionCommand,
  }
)

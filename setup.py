import sys
import os
import setuptools

from setuptools.command.install import install

version='0.9.1'

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
  python_requires='>=2.7.16, <4',
  install_requires=[
    'requests',
    'urllib3',
    'xxhash',
    'importlib-metadata ~= 1.0 ; python_version < "3.8"',
    'futures; python_version == "2.7"'
  ],
  extras_require={
    'dev': [
      'bump2version',
    ]
  },
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Multimedia :: Video',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
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

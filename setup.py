import sys
import os
import setuptools

from setuptools.command.install import install

version='2.0.0'

with open("README.md", "r") as f:
  long_description = f.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != version:
            info = f"Git tag: {tag} does not match the version of this app: {version}"
            sys.exit(info)

setuptools.setup(
  name='frameioclient',
  version=version,
  python_requires='>=3.6.5, <4',
  install_requires=[
    'analytics-python',
    'enlighten',
    'importlib-metadata ~= 1.0 ; python_version < "3.8"',
    'requests',
    'token-bucket',
    'urllib3',
    'xxhash',
  ],
  extras_require={
    'dev': [
      'bump2version',
      'sphinx',
      'sphinx-jekyll-builder'
    ]
  },
  entry_points ={
    'console_scripts': [
      'fiocli = frameioclient.fiocli:main'
    ]
  },
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Multimedia :: Video',
    'Topic :: Software Development :: Libraries',
    'License :: OSI Approved :: MIT License',
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

import setuptools

with open('README.md', 'r') as f:
  long_description = f.read()

setuptools.setup(
  name='frameioclient',
  version='0.7.0',
  python_requires='>=2.6, !=3.8.*, <4',
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
  license='MIT'
)

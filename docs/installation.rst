===============
frameioclient
===============

.. toctree::
    :hidden:

    installation

Installation
============

Stable releases of frameioclient can be installed with

.. code-block:: sh

    pip <http://pip.openplans.org> <- or you may download a `.tgz` source

archive from `pypi <http://pypi.python.org/pypi/frameioclient#downloads>`_.
See the :doc:`installation` page for more detailed instructions.

If you want to use the latest code, you can grab it from our
`Git repository <http://github.com/frameio/python-frameio-client>`_, or `fork it <http://github.com/jkeyes/python-intercom>`_.

Usage
===================================

Authorization
-------------

Frame.io Python SDK documentation: `Personal Access Tokens <https://developers.intercom.com/intercom-api-reference/reference#section-access-tokens>`_.


.. code-block:: python

    from frameioclient import FrameioClient
    client = FrameioClient(token='my-token')

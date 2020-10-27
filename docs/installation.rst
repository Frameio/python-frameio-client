===============
frameioclient
===============

.. toctree::
    :hidden:

    installation

Installation
============

Stable releases of python-intercom can be installed with
`pip <http://pip.openplans.org>`_ or you may download a `.tgz` source
archive from `pypi <http://pypi.python.org/pypi/python-intercom#downloads>`_.
See the :doc:`installation` page for more detailed instructions.

If you want to use the latest code, you can grab it from our
`Git repository <http://github.com/jkeyes/python-intercom>`_, or `fork it <http://github.com/jkeyes/python-intercom>`_.

Usage
===================================

Authorization
-------------

Frame.io Python SDK documentation: `Personal Access Tokens <https://developers.intercom.com/intercom-api-reference/reference#section-access-tokens>`_.

::

    from frameioclient import FrameioClient
    client = FrameioClient(token='my-token')

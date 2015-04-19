seqfile
=======

Generate sequential file names in a thread-safe way.

Use case
--------

If you want to create sequential files to write output to (say from
different threads or from consecutive runs of the same program), then
you can use this module.

Installing
----------

This package is available from PyPi_.

::

    pip install seqfile


You can install the latest version (bleeding edge) this way:

::

    pip install git+https://github.com/musically-ut/seqfile.git@master#egg=seqfile

Tests
-----

The tests can be run using ``nosetests`` or ``python setup.py test``.


.. _PyPi: https://pypi.python.org/pypi

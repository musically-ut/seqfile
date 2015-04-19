seqfile
=======

|BuildStatus|

Generate sequential file names in a thread-safe way.

Usage
-----

If you want to create sequential files to write output to (say from
different threads or from consecutive runs of the same program), then
you can use this module.

::

    # Assume files "./a.0.txt" and "./a.3.txt" exist.
    >> import seqfile

    # Providing prefix and suffix finds the next file in the sequence
    # ignoring any gaps
    >> seqfile.findNextFile('.', prefix='a.', suffix='.txt')
    './a.4.txt'

    # Providing a file name generator as fnameGen produces the first file
    # which it was successful in creating.
    >> seqfile.findNextFile('.', fnameGen=lambda x: 'a.' + str(x) + '.txt')
    './a.1.txt'

The returned file will exist, be empty, and can be opened for writing.


Installing
----------

This package is available from PyPi_.

::

    pip install seqfile


You can install the bleeding edge directly from the source:

::

    pip install git+https://github.com/musically-ut/seqfile.git@master#egg=seqfile

Tests
-----

The tests can be run using ``nosetests`` (if all dependencies are installed in
the environment) or using ``python setup.py test``.


.. _PyPi: https://pypi.python.org/pypi

.. |BuildStatus| image:: https://api.travis-ci.org/musically-ut/seqfile.svg
   :target: https://travis-ci.org/musically-ut/seqfile

seqfile
=======

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


You can install the latest version (bleeding edge) this way:

::

    pip install git+https://github.com/musically-ut/seqfile.git@master#egg=seqfile

Tests
-----

The tests can be run using ``nosetests`` or ``python setup.py test``.


.. _PyPi: https://pypi.python.org/pypi

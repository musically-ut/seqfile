seqfile
=======

|BuildStatus| |BuildStatusWin| |Coverage|

Generate sequential file names in a thread-safe way.

Usage
-----

If you want to create sequential files to write output to (say from
different threads or from consecutive runs of the same program), then
you can use this module from within your program or from the command
line.

From the commandline
~~~~~~~~~~~~~~~~~~~~

.. code:: sh

    $ seqfile
    usage: seqfile [-h] [-m MAX_ATTEMPTS] [-b BASE] prefix [suffix] [folder]
    seqfile: error: too few arguments

    # Assume files "./a.0.txt" and "./a.3.txt" exist.
    $ seqfile a. .txt .
    ./a.4.txt

    # Assume no other files exist.
    # This will create files 100 files with names test.*.txt in the current
    # folder.
    $ seq 100 | xargs -n 1 -P 100 -I{} \
        bash -c "fname=\$(seqfile test. .txt); \
                 echo 'Do something awesome with {}' > \$fname"

From your program
~~~~~~~~~~~~~~~~~

.. code:: python

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

This package is available from `PyPi <https://pypi.python.org/pypi/seqfile>`_.

::

    pip install seqfile

You can install the bleeding edge directly from the source:

::

    pip install git+https://github.com/musically-ut/seqfile.git@master#egg=seqfile

Tests
-----

The tests can be run using ``nosetests`` (if all dependencies are installed in
the environment) or using ``python setup.py test``.

Caveats
-------

It is best not to provide unicode characters in the ``prefix``, ``suffix``, or
``folder``. Though the support has been tested on all major OSes, it has not
been verfied that all OS/filesystem combinations will work.

Also, the ``O_CREAT | O_EXCEL`` trick used to create files atomically may not
work on old linux kernels while writing to an NFS.


.. |BuildStatus| image:: https://travis-ci.org/musically-ut/seqfile.svg?branch=master
   :target: https://travis-ci.org/musically-ut/seqfile
.. |BuildStatusWin| image:: https://ci.appveyor.com/api/projects/status/6x28l2cgqupdjyue/branch/master?svg=true
   :target: https://ci.appveyor.com/project/musically-ut/seqfile
.. |Coverage| image:: https://coveralls.io/repos/musically-ut/seqfile/badge.svg?branch=master
   :target: https://coveralls.io/r/musically-ut/seqfile?branch=master
.. |PythonVersions| image:: https://pypip.in/py_versions/seqfile/badge.svg
   :target: https://pypi.python.org/pypi/seqfile/
   :alt: Supported Python versions
.. |PyPiVersion| image:: https://pypip.in/version/seqfile/badge.svg
   :target: https://pypi.python.org/pypi/seqfile/
   :alt: Latest Version
.. |License| image:: https://pypip.in/license/seqfile/badge.svg
   :target: https://pypi.python.org/pypi/seqfile/
   :alt: License

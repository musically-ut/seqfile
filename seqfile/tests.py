import tempfile as _T
import shutil   as _shutil
import os       as _os
from . import seqfile as _S
from contextlib import contextmanager

join = _os.path.join

@contextmanager
def tempDir():
    d = _T.mkdtemp()
    try:
        yield d
    finally:
        _shutil.rmtree(d)


prefix, suffix = 'mdl.', '.cPickle'
fnameGen = lambda x : prefix + str(x) + suffix

###########################################################################################
## Tests
###########################################################################################

def test_findNextFile_0_base():
    with tempDir() as d:
        assert _S.findNextFile(folder=d, prefix=prefix, suffix=suffix, base=0) == join(d, prefix + str(0) + suffix)

def test_findNextFile_0_base_fnamegen():
    with tempDir() as d:
        assert _S.findNextFile(folder=d, fnameGen=fnameGen, base=0) == join(d, fnameGen(0))


def test_findNextFile_1_base():
    with tempDir() as d:
        assert _S.findNextFile(d, prefix, suffix, base=1) == join(d, fnameGen(1))

def test_findNextFile_1_base_fnamegen():
    with tempDir() as d:
        assert _S.findNextFile(folder=d, fnameGen=fnameGen, base=1) == join(d, fnameGen(1))


def test_findNextFile_with_file():
    with tempDir() as d:
        _S._doAtomicFileCreation( join(d, fnameGen(0)) )
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(1))

def test_findNextFile_with_file_fnamegen():
    with tempDir() as d:
        _S._doAtomicFileCreation( join(d, fnameGen(0)) )
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(1))

def test_findNextFile_with_files():
    with tempDir() as d:
        _S._doAtomicFileCreation( join(d, fnameGen(0)) )
        _S._doAtomicFileCreation( join(d, fnameGen(1)) )
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(2))

def test_findNextFile_with_files_fnamegen():
    with tempDir() as d:
        _S._doAtomicFileCreation( join(d, fnameGen(0)) )
        _S._doAtomicFileCreation( join(d, fnameGen(1)) )
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(2))

def test_findNextFile_many_files():
    with tempDir() as d:
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(0))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(1))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(2))

def test_findNextFile_many_files_fnamegen():
    with tempDir() as d:
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(0))
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(1))
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(2))

# These tests show the difference between prefix/suffix and fnameGen method.

def test_findNextFile_with_files_non_consecutive():
    with tempDir() as d:
        _S._doAtomicFileCreation( join(d, fnameGen(0)) )
        _S._doAtomicFileCreation( join(d, fnameGen(2)) )
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(3))

def test_findNextFile_with_files_non_consecutive_fnamegen():
    with tempDir() as d:
        _S._doAtomicFileCreation( join(d, fnameGen(0)) )
        _S._doAtomicFileCreation( join(d, fnameGen(2)) )
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(1))


###########################################################################################
## Concurrency Tests
###########################################################################################

## Warning: These tests monkey patch the seqfile.seqfile module!
## Hence, these tests must be run last.

import seqfile as _SS

# Monkey patch _doAtomicFileCreation for testing
_SS._oldAtomicCreation = _SS._doAtomicFileCreation
def _testAtomicCreationFactory(folder):

    def _testAtomicCreation(filePath):
        # Create only the first file in the sequence
        if filePath == join(folder, fnameGen(0)):
            # Create the file to simulate concurrent file creation
            _os.close( _os.open( filePath, _os.O_CREAT | _os.O_EXCL ) )

        return _SS._oldAtomicCreation(filePath)

    return _testAtomicCreation


def test_findNextFile_concurrent():
    with tempDir() as d:
        _SS._doAtomicFileCreation = _testAtomicCreationFactory(d)
        # File created must be the second file in the sequence
        assert _SS.findNextFile(d, prefix, suffix) == join(d, fnameGen(1))



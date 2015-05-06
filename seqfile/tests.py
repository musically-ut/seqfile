# -*- coding: utf-8 -*-
import tempfile as _T
import shutil as _shutil
import os as _os
import glob as _glob
from io import StringIO as _StringIO

from nose.tools import raises
from . import seqfile as _S
from contextlib import contextmanager
import pep8


@contextmanager
def tempDir(prefix=None):
    prefix = '' if prefix is None else prefix
    d = _T.mkdtemp(prefix=prefix)
    try:
        yield d
    finally:
        _shutil.rmtree(d)


def fnameGen(x): return prefix + str(x) + suffix


def execRun(*args):
    stderr, stdout = _StringIO(), _StringIO()
    _S._run(args, stderr, stdout)
    return stderr.getvalue().strip(), stdout.getvalue().strip()


prefix, suffix = 'mdl.', '.cPickle'
join = _os.path.join


###############################################################################
# Tests
###############################################################################

def test_pep8_conformance():
    """Test that we conform to PEP8."""
    pep8style = pep8.StyleGuide()
    result = pep8style.check_files(_glob.glob('./seqfile/*.py'))
    assert result.total_errors == 0


@raises(OSError)
def test_findNextFile_non_existant_destination():
    with tempDir() as d:
        _S.findNextFile(folder=d + '-non-existent', fnameGen=fnameGen)


@raises(RuntimeError)
def test_findNextFile_too_many_arguments():
    with tempDir() as d:
        _S.findNextFile(d, fnameGen=fnameGen, prefix=prefix, suffix=suffix)


@raises(RuntimeError)
def test_findNextFile_too_few_arguments():
    with tempDir() as d:
        _S.findNextFile(d)


def test_findNextFile_0_base():
    with tempDir() as d:
        assert _S.findNextFile(d, prefix=prefix, suffix=suffix, base=0) == \
               join(d, prefix + str(0) + suffix)


def test_findNextFile_0_base_exec():
    with tempDir() as d:
        stderr, stdout = execRun(prefix, suffix, d)
        assert stdout == join(d, prefix + str(0) + suffix)


def test_findNextFile_0_base_fnamegen():
    with tempDir() as d:
        assert _S.findNextFile(folder=d, fnameGen=fnameGen, base=0) == \
               join(d, fnameGen(0))


def test_findNextFile_1_base():
    with tempDir() as d:
        assert _S.findNextFile(d, prefix, suffix, base=1) == \
               join(d, fnameGen(1))


def test_findNextFile_1_base_exec():
    with tempDir() as d:
        stderr, stdout = execRun(prefix, suffix, d, "--base=1")
        assert stdout == join(d, prefix + str(1) + suffix)


def test_findNextFile_1_base_fnamegen():
    with tempDir() as d:
        assert _S.findNextFile(folder=d, fnameGen=fnameGen, base=1) == \
               join(d, fnameGen(1))


def test_findNextFile_with_file():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(1))


def test_findNextFile_with_file_fnamegen():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(1))


def test_findNextFile_with_files():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        _S._doAtomicFileCreation(join(d, fnameGen(1)))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(2))


def test_findNextFile_with_noisy_files():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        _S._doAtomicFileCreation(join(d, fnameGen(1)))
        _S._doAtomicFileCreation(join(d, fnameGen('bar')))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(2))


def test_findNextFile_with_regex_compat_files():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0).replace('.', 'X')))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(0))


def test_findNextFile_with_files_fnamegen():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        _S._doAtomicFileCreation(join(d, fnameGen(1)))
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
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        _S._doAtomicFileCreation(join(d, fnameGen(2)))
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(3))


def test_findNextFile_with_files_non_consecutive_fnamegen():
    with tempDir() as d:
        _S._doAtomicFileCreation(join(d, fnameGen(0)))
        _S._doAtomicFileCreation(join(d, fnameGen(2)))
        assert _S.findNextFile(d, fnameGen=fnameGen) == join(d, fnameGen(1))


def test_findNextFile_with_unicode():
    with tempDir() as d:
        prefix, suffix = u'ü', u'.é'
        assert (_S.findNextFile(d, prefix, suffix) ==
                join(d, prefix + '0' + suffix))


def test_findNextFile_with_unicode_fnamegen():
    with tempDir() as d:
        prefix, suffix = u'ü', u'.é'

        def fnameGen(x): return prefix + str(x) + suffix
        assert (_S.findNextFile(d, fnameGen=fnameGen) ==
                join(d, prefix + '0' + suffix))


def test_findNextFile_with_unicode_with_files():
    with tempDir() as d:
        prefix, suffix = u'ü', u'.é'
        _S._doAtomicFileCreation(join(d,  prefix + '0' + suffix))
        assert (_S.findNextFile(d, prefix, suffix) ==
                join(d, prefix + '1' + suffix))


def test_findNextFile_with_unicode_with_files_fnameGen():
    with tempDir() as d:
        prefix, suffix = u'ü', u'.é'

        def fnameGen(x): return prefix + str(x) + suffix
        _S._doAtomicFileCreation(join(d,  fnameGen(0)))
        assert (_S.findNextFile(d, prefix, suffix) ==
                join(d, prefix + '1' + suffix))


def test_findNextFile_with_unicode_folder():
    with tempDir(u'ü') as d:
        prefix, suffix = u'ü', u'.é'
        assert (_S.findNextFile(d, prefix, suffix) ==
                join(d, prefix + '0' + suffix))


###############################################################################
# Concurrency Tests
###############################################################################

# Warning: These tests monkey patch the seqfile.seqfile module!
# Hence, these tests must be run last.

# Monkey patch _doAtomicFileCreation for testing
_S._oldAtomicCreation = _S._doAtomicFileCreation


def _testAtomicCreationFactory(predicate):

    def _testAtomicCreation(filePath):
        # Create only the first file in the sequence
        if predicate(filePath):
            # Create the file to simulate concurrent file creation
            _os.close(_os.open(filePath, _os.O_CREAT | _os.O_EXCL))

        return _S._oldAtomicCreation(filePath)

    return _testAtomicCreation


def test_findNextFile_concurrent():
    with tempDir() as d:
        def predicate(filePath): return filePath == join(d, fnameGen(0))
        _S._doAtomicFileCreation = _testAtomicCreationFactory(predicate)
        # File created must be the second file in the sequence
        assert _S.findNextFile(d, prefix, suffix) == join(d, fnameGen(1))


@raises(OSError)
def test_findNextFile_concurrent_max_attempts_fail():
    with tempDir() as d:
        # Always create the file, maxattempts will be exhausted
        def predicate(_filePath): return True
        _S._doAtomicFileCreation = _testAtomicCreationFactory(predicate)
        _S.findNextFile(d, prefix, suffix)


@raises(OSError)
def test_findNextFile_concurrent_max_attempts_fail_unicode_folder():
    with tempDir(u'ü') as d:
        # Always create the file, maxattempts will be exhausted
        def predicate(_filePath): return True
        _S._doAtomicFileCreation = _testAtomicCreationFactory(predicate)
        _S.findNextFile(d, prefix, suffix)


@raises(SystemExit)
def test_findNextFile_exec_concurrent_max_attempts_fail():
    with tempDir() as d:
        # Always create the file, maxattempts will be exhausted
        def predicate(_filePath): return True
        _S._doAtomicFileCreation = _testAtomicCreationFactory(predicate)
        execRun(prefix, suffix, d)

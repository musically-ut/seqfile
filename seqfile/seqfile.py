import os      as _os
import re      as _re
import glob    as _glob
import natsort as _natsort

def _getStrBetween(prefix, s, suffix):
    """Return the value inside s between prefix and suffix."""
    preIdx = s.index(prefix)
    sufIdx = s.index(suffix)

    return s[preIdx + len(prefix):sufIdx]

def _doAtomicFileCreation(filePath):
    """Atomically tries to create the file."""
    try:
        _os.close(_os.open(filePath, _os.O_CREAT | _os.O_EXCL))
        return True
    except OSError:
        return False


def _findNextFile(folder, prefix, suffix, fnameGen, base, maxattempts, loop):
    if loop >= maxattempts:
        raise OSError('Unable to create file after ' + str(maxattempts) + ' attempts.')

    if prefix is None and fnameGen is None:
        raise ValueError("Need at least one of prefix or fnameGen to proceed.")

    if (prefix is not None or suffix is not None) and fnameGen is not None:
        raise ValueError("Cannot provide prefix/suffix as well as an fnameGen.")

    nextFileIdx = base

    if fnameGen is not None:
        while _os.path.exists(_os.path.join(folder, fnameGen(nextFileIdx))):
            nextFileIdx += 1

    if prefix is not None or suffix is not None:
        prefix = prefix if prefix is not None else ''
        suffix = suffix if suffix is not None else ''

        globPattern = lambda x : _os.path.join(folder, prefix + x + suffix)
        allFiles = _natsort.natsorted(_glob.glob(globPattern('*')), alg=_natsort.ns.INT)
        selectFilesRegEx = _re.compile(globPattern('[0-9]+'))
        numberedFiles = [ f for f in allFiles if _re.match(selectFilesRegEx, f) ]

        if len(numberedFiles) > 0:
            nextFileIdx = int(_getStrBetween(prefix, numberedFiles[-1], suffix)) + 1


    if fnameGen is None:
        retFileName = _os.path.join(folder, prefix + str(nextFileIdx) + suffix)
    else:
        retFileName = _os.path.join(folder, fnameGen(nextFileIdx))

    if _doAtomicFileCreation(retFileName):
        return retFileName
    else:
        return _findNextFile(folder, prefix, suffix, fnameGen, base, maxattempts, loop + 1)



###########################################################################################
## Public interface
###########################################################################################


def findNextFile(folder='.', prefix=None, suffix=None, fnameGen=None, base=0, maxattempts=10):
    """
    Finds the next available file-name in the given folder. This function is not thread safe.

    Args:
        prefix      - prefix of the file to be generated (default: '')
        suffix      - suffix of the file to be generated (default: '')
        fnameGen    - function which generates the filenames (default: None)
        folder      - string which has path to the folder where the file should be created (default: '.')
        base        - the first index to count (default: 0)
        maxattempts - number of attempts to create the file before failing with OSError (default: 10)

    Returns:
        Path of the file which follows the provided pattern and can be written to.

    Raises:
        RuntimeError - If an incorrect combination of arguments is provided.
        OSError      - If is unable to create a file on the disk.
    """
    return _findNextFile(folder, prefix, suffix, fnameGen, base, maxattempts, 0)



import os      as _os
import re      as _re
import glob    as _glob
import errno   as _errno
import natsort as _natsort

def _getStrBetween(prefix, s, suffix):
    """Return the value inside s between prefix and suffix."""
    preIdx = s.index(prefix)
    sufIdx = s.index(suffix)

    return s[preIdx + len(prefix):sufIdx]

def _doAtomicFileCreation(filePath):
    """Tries to atomically create the requested file."""
    try:
        _os.close(_os.open(filePath, _os.O_CREAT | _os.O_EXCL))
        return True
    except OSError as e:
        if e.errno == _errno.EEXIST:
            return False
        else:
            raise e


def _findNextFile(folder, prefix, suffix, fnameGen, base, maxattempts, loop):
    if loop >= maxattempts:
        raise OSError("Unable to create file at " + folder + " after " + str(maxattempts) + " attempts.")

    if prefix is None and fnameGen is None:
        raise RuntimeError("Need at least one of prefix or fnameGen to proceed.")

    if (prefix is not None or suffix is not None) and fnameGen is not None:
        raise RuntimeError("Cannot provide prefix/suffix as well as an fnameGen.")

    nextFileIdx = base

    if fnameGen is not None:
        while _os.path.exists(_os.path.join(folder, fnameGen(nextFileIdx))):
            nextFileIdx += 1

    if prefix is not None or suffix is not None:
        prefix = prefix if prefix is not None else ''
        suffix = suffix if suffix is not None else ''

        globPattern = lambda x : _os.path.join(folder, prefix + x + suffix)
        allFiles = _natsort.natsorted(_glob.glob(globPattern('*')), alg=_natsort.ns.INT)
        # Not using complete path here, since Windows paths contain
        # back-slashes, which will be interpreted as escaped special regex.
        selectFilesRegEx = _re.compile(prefix + '[0-9]+' + suffix + '$')
        numberedFiles = [ f for f in allFiles if _re.search(selectFilesRegEx, f) ]

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
    """Finds the next available file-name in a sequence.

    This function will create a file of zero size and will return a path to it
    to the caller. No files which exist will be harmed in this operation and
    concurrent executions of this function will return separate files. In case
    of conflict, the function will attempt to generate a new file name up to
    maxattempts number of times before failing.

    The sequence will start from the base argument (default: 0).

    If used with the prefix/suffix form, it will look for the next file in the
    sequence ignoring any gaps in the sequence. Hence, if the files "a.0.txt"
    and "a.3.txt" exist, then the next file returned will be "a.4.txt" when
    called with prefix="a." and suffix=".txt".

    In case fnameGen is provided, the first generated filename which does not
    exist will be created and its path will be returned. Hence, if the files
    "a.0.txt" and "a.3.txt" exist, then the next file returned will be
    "a.1.txt" if called with fnameGen = lambda x : "a." + str(x) + ".txt"


    Args:
        folder      - string which has path to the folder where the file should be created (default: '.')
        prefix      - prefix of the file to be generated (default: '')
        suffix      - suffix of the file to be generated (default: '')
        fnameGen    - function which generates the filenames given a number as input (default: None)
        base        - the first index to count (default: 0)
        maxattempts - number of attempts to create the file before failing with OSError (default: 10)

    Returns:
        Path of the file which follows the provided pattern and can be written to.

    Raises:
        RuntimeError - If an incorrect combination of arguments is provided.
        OSError      - If is unable to create a file (wrong path, drive full, etc.).
    """
    expFolder = _os.path.expanduser(_os.path.expandvars(folder))
    return _findNextFile(expFolder, prefix, suffix, fnameGen, base, maxattempts, 0)



import os as _os
import re as _re
import glob as _glob
import errno as _errno
import unicodedata as _u
import sys as _sys

import argparse as _argparse
import natsort as _natsort


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
        raise OSError(_errno.EEXIST,
                      "Unable to create file at " + folder +
                      " after " + str(maxattempts) + " attempts.")

    if prefix is None and fnameGen is None:
        raise RuntimeError("Need at least one of prefix/suffix or fnameGen.")

    if (prefix is not None or suffix is not None) and fnameGen is not None:
        raise RuntimeError("Cannot provide both prefix/suffix and a fnameGen.")

    nextFileIdx = base

    if fnameGen is not None:
        while _os.path.exists(_os.path.join(folder, fnameGen(nextFileIdx))):
            nextFileIdx += 1

    if prefix is not None or suffix is not None:
        prefix = prefix if prefix is not None else u''
        suffix = suffix if suffix is not None else u''

        globPattern = _os.path.join(folder, prefix + u'*' + suffix)
        rawRegEx = prefix + u'([0-9]+)' + suffix + u'$'

        # Mac uses NFD normalization for Unicode filenames while windows and
        # linux use NFC normalization.
        if _sys.platform.startswith('darwin'):
            normalizedGlobPattern = _u.normalize('NFD', globPattern)
            normalizedRegEx = _u.normalize('NFD', rawRegEx)
        else:
            normalizedGlobPattern = _u.normalize('NFC', globPattern)
            normalizedRegEx = _u.normalize('NFC', rawRegEx)

        allFiles = _glob.glob(normalizedGlobPattern)
        sortedFiles = _natsort.natsorted(allFiles,
                                         alg=_natsort.ns.INT,
                                         reverse=True)

        numFilesRegEx = _re.compile(normalizedRegEx, _re.UNICODE)
        numberedFiles = (_re.search(numFilesRegEx, f) for f in sortedFiles
                         if _re.search(numFilesRegEx, f))
        lastNumberedFile = next(numberedFiles, None)

        if lastNumberedFile is not None:
            lastFileNum = int(lastNumberedFile.group(1))
            nextFileIdx = lastFileNum + 1

    if fnameGen is None:
        retFileName = _os.path.join(folder, prefix + str(nextFileIdx) + suffix)
    else:
        retFileName = _os.path.join(folder, fnameGen(nextFileIdx))

    if _doAtomicFileCreation(retFileName):
        return retFileName
    else:
        return _findNextFile(folder, prefix, suffix, fnameGen,
                             base, maxattempts, loop + 1)


###############################################################################
# Public interface
###############################################################################


def findNextFile(folder='.',
                 prefix=None,
                 suffix=None,
                 fnameGen=None,
                 base=0,
                 maxattempts=10):
    """Finds the next available file-name in a sequence.

    This function will create a file of zero size and will return the path to
    it to the caller. No files which exist will be altered in this operation
    and concurrent executions of this function will return separate files. In
    case of conflict, the function will attempt to generate a new file name up
    to maxattempts number of times before failing.

    The sequence will start from the base argument (default: 0).

    If used with the prefix/suffix, it will look for the next file in the
    sequence ignoring any gaps. Hence, if the files "a.0.txt" and "a.3.txt"
    exist, then the next file returned will be "a.4.txt" when called with
    prefix="a." and suffix=".txt".

    In case fnameGen is provided, the first generated filename which does not
    exist will be created and its path will be returned. Hence, if the files
    "a.0.txt" and "a.3.txt" exist, then the next file returned will be
    "a.1.txt" when called with fnameGen = lambda x : "a." + str(x) + ".txt"

    Args:
        folder      - string which has path to the folder where the file should
                      be created (default: '.')
        prefix      - prefix of the file to be generated (default: '')
        suffix      - suffix of the file to be generated (default: '')
        fnameGen    - function which generates the filenames given a number as
                      input (default: None)
        base        - the first index to count (default: 0)
        maxattempts - number of attempts to create the file before failing with
                      OSError (default: 10)

    Returns:
        Path of the file which follows the provided pattern and can be opened
        for writing.

    Raises:
        RuntimeError - If an incorrect combination of arguments is provided.
        OSError      - If is unable to create a file (wrong path, drive full,
                       illegal character in filename, etc.).
    """
    expFolder = _os.path.expanduser(_os.path.expandvars(folder))
    return _findNextFile(expFolder, prefix, suffix, fnameGen,
                         base, maxattempts, 0)


def _run(passedArgs=None, stderr=None, stdout=None, exitFn=None):
    """Executes the script, gets prefix/suffix from the command prompt and
    produces output on STDOUT. For help with command line options, invoke
    script with '--help'.
    """

    description = """Finds the next available file-name in a sequence.

    This program will create a file of zero size and will output the path to it
    on STDOUT. No files which exist will be altered in this operation and
    concurrent invocations of this program will return separate files. In case
    of conflict, this program will attempt to generate a new file name up to
    'maxattempts' number of times before failing. (See --max-attempts)

    The sequence will start from the base argument (See --base, default: 0).

    This program will look for the next file in the sequence ignoring any gaps.
    Hence, if the files "a.0.txt" and "a.3.txt" exist, then the next file
    returned will be "a.4.txt" when called with prefix="a." and suffix=".txt".

    Returns:
        Path of the file which follows the provided pattern and can be opened
        for writing.

        Otherwise, it prints an error (wrong path, drive full, illegal
        character in filename, etc.) to stderr and exits with a non-zero error
        code.
    """

    argParser = _argparse.ArgumentParser(
            description=description,
            formatter_class=_argparse.RawTextHelpFormatter)

    argParser.add_argument('prefix',
                           help='Prefix for the sequence of files.')
    argParser.add_argument('suffix',
                           help='Suffix for the sequence of files.',
                           nargs='?',
                           default='')
    argParser.add_argument('folder',
                           help='The folder where the file will be created.',
                           nargs='?',
                           default=_os.getcwd())
    argParser.add_argument('-m', '--max-attempts',
                           help='Number of attempts to make before giving up.',
                           default=10)
    argParser.add_argument('-b', '--base',
                           help='From where to start counting (default: 0).',
                           default=0)

    passedArgs = passedArgs if passedArgs is not None else _sys.argv[1:]
    args = argParser.parse_args(passedArgs)

    stdout = _sys.stdout if stdout is None else stdout
    stderr = _sys.stderr if stderr is None else stderr

    try:
        nextFile = findNextFile(args.folder, prefix=args.prefix,
                                suffix=args.suffix,
                                maxattempts=args.max_attempts,
                                base=args.base)
        # The newline will be converted to the correct platform specific line
        # ending as `sys.stdout` is opened in non-binary mode.
        # Hence, we do not need to explicitly print out `\r\n` for Windows.
        stdout.write(nextFile + '\n')
    except OSError as e:
        stderr.write(_os.strerror(e.errno) + '\n')
        _sys.exit(e.errno)

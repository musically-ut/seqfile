import os
from setuptools import setup

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name             = "seqfile",
    version          = "0.0.1",
    author           = "Utkarsh Upadhyay",
    author_email     = "musically.ut@gmail.com",
    description      = ("Find the next file in a sequence of files in a thread-safe way."),
    license          = "MIT",
    keywords         = "file threadsafe sequence",
    url              = "https://github.com/musically-ut/seqfile",
    packages         = ['seqfile'],
    setup_requires   = ['nose>=1.0', 'natsort>=3.5.6'],
    test_suite       = 'nose.collector',
    long_description = read('README.rst'),
    classifiers      = [
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        "Natural Language :: English",
    ],
)

from __future__ import absolute_import
from .seqfile import findNextFile

import pkg_resources as _pkg

__version__ = _pkg.get_distribution("seqfile").version

__all__ = [ 'findNextFile' ]

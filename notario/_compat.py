"""
A basic module to provide both Python2 and Python3 support
on the same source
"""
import sys

if sys.version_info >= (3, 0): # pragma: no cover
    basestring = str
else:
    basestring = basestring

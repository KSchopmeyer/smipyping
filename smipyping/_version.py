# There are submodules, but clients shouldn't need to know about them.
# Importing just this module is enough.
# These are explicitly safe for 'import *'

"""
Version of the smipyping package.
"""

#: Version of the smipyping package, as a :term:`string`.
#:
#: Possible formats for the version string are:
#:
#: * "M.N.U.dev0": During development of future M.N.U release (not released to
#:   PyPI)
#: * "M.N.U.rcX": Release candidate X of future M.N.U release (not released to
#:   PyPI)
#: * "M.N.U": The final M.N.U release
__version__ = '0.6.0.dev0'

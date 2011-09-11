import logging
import os

import zc.buildout

log = logging.getLogger('libjpeg hook')

def pre_make(options, buildout):
    """Custom pre-make hook for building libjpeg."""
    # The installation procedure is arrogant enough to expect all the
    # directories to exist and fails otherwise.
    for dir in ('bin', 'man/man1', 'include', 'lib'):
        os.makedirs(os.path.join(options['location'], dir))

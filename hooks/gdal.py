import logging
import shutil
import os
import re

import zc.buildout

log = logging.getLogger('GDAL hook')

def substitute(filename, search_re, replacement):
    """Substitutes text within the contents of ``filename`` matching
    ``search_re`` with ``replacement``.
    """
    search = re.compile(search_re, re.MULTILINE)
    text = open(filename).read()
    text = replacement.join(search.split(text))
    
    newfilename = '%s%s' % (filename, '.~new')
    newfile = open(newfilename, 'w')
    newfile.write(text)
    newfile.close()
    shutil.copymode(filename, newfilename)
    shutil.move(newfilename, filename)


def post_make(options, buildout):
    """Custom post-make hook for bulding GDAL python bindings."""
    # Generate rpath information..
    rpath = ['%s/lib' % buildout[part]['location']
             for part
             in ('geos','proj','postgresql','libpng','libtiff','libgif','libjpeg','curl')
             ] + ['%s/lib' % options['location']]

    # ..and push it into the setup file
    substitute('setup.py',
               'extra_link_args=EXTRA_LINK_ARGS,',
               'extra_link_args=EXTRA_LINK_ARGS, runtime_library_dirs=%s' % str(rpath))
    
#    cmd = '%s setup.py install' % buildout[buildout['buildout']['python']]['executable']
#    log.info('Installing GDAL python bindings')

#    if os.system(cmd):
#        log.error('Error executing command: %s' % cmd)
#        raise zc.buildout.UserError('System error')


import logging
import shutil
import sys
import re
import os

import zc.buildout

log = logging.getLogger('MapServer hook')

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

def run(cmd):
    if os.system(cmd):
        log.error('Error executing command: %s' % cmd)
        raise zc.buildout.UserError('System error')


def pre_make(options, buildout):
    """Custom pre-make hook for patching MapServer."""
    if sys.platform.lower() == 'darwin':
        log.info('Patching Makefile for OSX compliance')
        substitute('Makefile', 'THREAD=-DUSE_THREAD', 'THREAD=-DUSE_THREAD -Dunix'),
        substitute('Makefile', '^LD=\s+gcc', 'LD=g++')

def post_make(options, buildout):
    """Custom post-make hook for installing python mapscript."""
    here = os.getcwd()
    os.chdir('mapscript/python')

    try:
        log.info('Installing python mapscript')

        # Generate rpath information..
        rpath = ['%s/lib' % buildout[part]['location']
                 for part
                 in ('geos','proj','postgresql','libpng','libtiff','libgif',
                     'libjpeg','curl','postgis','libgd','freetype','gdal')
                 ]

        # ..and push it into the setup file
        substitute('setup.py',
                   'extra_link_args = extras,',
                   'extra_link_args = extras, runtime_library_dirs=%s' % str(rpath))

        run('%s -modern -python -o mapscript_wrap.c ../mapscript.i' % options['swig'])
        run('sed -ie \'s/distutils.core/setuptools/\' setup.py')
    finally:
        os.chdir(here)

def post_make_deb(options, buildout):
    """Custom post-make hook for installing python mapscript."""
    here = os.getcwd()
    os.chdir('mapscript/python')

    try:
        log.info('Installing python mapscript')

        # Generate rpath information..
        rpath = ['%s/lib' % buildout[part]['location']
                 for part
                 in ('postgresql','postgis')
                 ]

        # ..and push it into the setup file
        substitute('setup.py',
                   'extra_link_args = extras,',
                   'extra_link_args = extras, runtime_library_dirs=%s' % str(rpath))

        run('%s -modern -python -o mapscript_wrap.c ../mapscript.i' % options['swig'])
        run('sed -ie \'s/distutils.core/setuptools/\' setup.py')
    finally:
        os.chdir(here)

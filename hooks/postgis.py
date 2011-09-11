import logging
import shutil
import re

import zc.buildout

log = logging.getLogger('PostGIS hook')

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

def pre_make(options, buildout):
    """Custom pre-make hook for patching PostGIS."""
    # ``make install`` fails because it tries to write files under
    # /etc. This will write under the corresponding parts directory
    # instead.
    substitute('extras/template_gis/Makefile',
               '\$\(DESTDIR\)',
               '$(prefix)')

    # Put in rpath info
    rpath = '-Wl,-rpath,%(geos)s,-rpath,%(proj)s,-rpath,%(postgres)s' % dict(
        geos='%s/lib' % buildout['geos']['location'],
        proj='%s/lib' % buildout['proj']['location'],
        postgres='%s/lib' % buildout['postgresql']['location']
        )
    substitute('Makefile.config',
               'DLFLAGS=-shared',
               'DLFLAGS=-shared %s' % rpath)

def pre_make_deb(options, buildout):
    """Custom pre-make hook for patching PostGIS."""
    # ``make install`` fails because it tries to write files under
    # /etc. This will write under the corresponding parts directory
    # instead.
    substitute('extras/template_gis/Makefile',
               '\$\(DESTDIR\)',
               '$(prefix)')

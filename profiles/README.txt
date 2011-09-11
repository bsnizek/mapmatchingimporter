============================================
Python Cartographic Library (PCL) - Buildout
============================================

This is a buildout system for the Python Cartographic Library (PCL)
software suite. Its main purpose is to provide a dependable and
repeatable way for developers to easily setup a development
environment that contains all dependencies.

Although geared towards developers the end result of the buildout is a
working environment containing the PCL components which may also be
used for non-development purposes.

The buildout provides an isolated sandbox environment for using and
developing PCL without interfering with the rest of your system.

The buildout is implemented using zc.buildout_

_zc.buildout: http://pypi.python.org/pypi/zc.buildout


Quickstart
----------

The following commands will install the whole of PCL, setup a
PostgreSQL db for testing and run the full test suite. For detailed
instructions read below.

 $ svn co http://svn.gispython.org/svn/gispy/buildout/pcl.buildout/trunk pcl.buildout
 $ python bootstrap.py
 $ ./bin/buildout
 $ python init_postgresql.py
 $ ./bin/test_core
 $ ./bin/test_gdal
 $ ./bin/test_georss
 $ ./bin/test_mapserver


Bootstrapping the buildout
--------------------------

When the buildout is checked out from the repository it needs to be
bootstrapped before it is ready to use. Simply run::

  $ python bootstrap.py

in the root of the buildout to get everything ready for work. This
will not build PCL, but will set the necessary scripts in the right
places for doing it.

After the bootstrapping you will have the buildout script in::

  ./bin/buildout

which is used to run the actual buildout process. For a full listing
of available options see::

  ./bin/buildout --help


Buildout structure
-------------------

The buildout is divided into smaller parts that correspond directly to
the components of PCL:

 - PCL-Core -- the core functionality
 - PCL-GDAL -- disk oriented data access using GDAL
 - PCL-MapServer -- MapServer based rendering engine
 - PCL-GeoRSS -- GeoRSS data source

Each component has its own buildout configuration (.cfg) file named
after the component. A developer wishing to work on a particular
component of PCL can build only the necessary components and avoid the
cost of having to build the whole of PCL.

To build a specific component you can simply run::

  ./bin/buildout -c [component].cfg

For example, to build PCL-Core you would run::

  ./bin/buildout -c pcl-core.cfg

After building a single component, you will have a script to run the
corresponding test suite::

  ./bin/test

You can optionally build the whole PCL suite by simply calling the
buildout script without any parameters::

  ./bin/buildout

Building the whole PCL will give you invidual scripts for running the
test suites of the components.


Dependencies
------------

PCL has a lot of dependencies on external libraries and programs. The
dependencies are defined in the ``dependencies.cfg`` configuration
file which the components of the buildout depend on.

You may wish to edit the dependencies configuration for two reasons:

 - change the version, download url, etc of a component
 - omit a component in favor of an already installed system component
   (e.g. a library)

Please note that if you do the latter, you may need to update the
sections using the component to make sure that paths are set
correctly.


Setting up PostgreSQL
---------------------

PCL-Core contains code and tests that interacts with a PostgreSQL
database. The buildout compiles the database server automatically, but
test data must be populated with a manual step.

In the root of the buildout directory is a python script called
``init_postgresql.py`` that takes care of setting up a database for
testing PCL. You can run by simply calling::

  $ ./bin/python init_postgresql.py 

You can optionally set the port number by using the --port option. The
default port is 5432.

You can run the script as many times as you want, but be aware that it
will reset the whole database. You shouldn't use the test database to
store any important data as it will be lost on subsequent runs of the
script.

See the OSX Notes section below if you are using Mac OSX.


Developing PCL
--------------

All the PCL components will be installed as development eggs, so you
can keep modifying the source on-the-fly. All editable source code is
located under the ``src/`` directory within the buildout.

There is also a Python interpreter script located in::

  ./bin/python

which has all the relevant components available for instant use. For
example, if you built PCL-Core the following will work without having
to modify any paths or whatsoever::

  ./bin/python
  >>> import cartography


OSX Notes
---------

Running the PostgreSQL database server on Mac OS X may require
modifying the amount of shared memory available on your system. See

  http://www.postgresql.org/docs/8.2/static/kernel-resources.html#SYSVIPC

for more detailed instructions.

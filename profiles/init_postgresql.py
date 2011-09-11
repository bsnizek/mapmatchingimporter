"""PostgreSQL initialization script

Note that existing configuration including data will be reset.
"""
import os
import sys
import stat
import time
import shutil

from optparse import OptionParser

container = os.getcwd()
PGDATA = os.path.join(container, 'var', 'postgresql')
PGROOT = os.path.join(container, 'parts', 'postgresql')
PGDBNAME = 'pcl_test'
POSTGIS = os.path.join(container, 'parts', 'postgis')
DATASET = os.path.join(container, 'parts', 'worldborders', 'world_borders.shp')

wrapper_script = os.path.join(container, 'bin', 'pg_ctl')
wrapper_script_tmpl = """\
#!/bin/sh
PGDATA=%s %s/bin/pg_ctl $@
""" 

test_env_tmpl = """\
[test-environment]
PCLCORE_DSN = host=localhost dbname=pcl_test port=%(port)s
"""

def system(cmd):
    if os.system(cmd):
        raise RuntimeError('Error running command: %s' % cmd)

def initpg(port):
    """Initializes a test PostgreSQL server."""
    # Shut down the server if it is running
    PIDFILE = '%s/postmaster.pid' % PGDATA
    if os.path.exists(wrapper_script) and os.path.exists(PIDFILE):
        print 'Shutting down PostgreSQL server...'
        system('%s stop' % wrapper_script)
        while os.path.exists(PIDFILE):
            time.sleep(1)

    # Clean up existing parts
    if os.path.exists(PGDATA):
        shutil.rmtree(PGDATA)

    assert not os.path.exists(PGDATA)
    os.makedirs(PGDATA)

    # Initialize the database
    system('%s/bin/initdb --auth=trust -D %s' % (PGROOT, PGDATA))

    # Create a wrapper script for pg_ctl
    wrapper = open(wrapper_script, 'w')
    wrapper.write(wrapper_script_tmpl % (PGDATA, PGROOT))
    wrapper.close()
    os.chmod(wrapper_script, stat.S_IRWXU)

    # Update the port setting and start up the server
    conffile = '%s/postgresql.conf' % PGDATA
    f = open(conffile)
    conf = ('port = %s' % port).join(f.read().split('#port = 5432'))
    f.close()
    open(conffile, 'w').write(conf)
    system('%s start' % wrapper_script)
    time.sleep(2)

    # Convert the shapefile data to SQL insert statements
    system('%s/bin/shp2pgsql -I -s 4269 %s postgis.world_borders > /tmp/wb.sql' % (POSTGIS, DATASET))

    # Create the test database
    system('%s/bin/createdb --port=%s %s' % (PGROOT, port, PGDBNAME))
    system('%s/bin/createlang --port=%s plpgsql %s' % (PGROOT, port, PGDBNAME))
    system('%s/bin/psql -p %s -d %s -c "CREATE SCHEMA postgis"' % (PGROOT, port, PGDBNAME))
    system('%s/bin/psql -p %s -d %s -f %s/share/lwpostgis.sql' % (PGROOT, port, PGDBNAME, POSTGIS))
    system('%s/bin/psql -p %s -d %s -f %s/share/spatial_ref_sys.sql' % (PGROOT, port, PGDBNAME, POSTGIS))

    # Import the data
    system('%s/bin/psql -p %s -d %s -f /tmp/wb.sql' % (PGROOT, port, PGDBNAME))
    system('%s/bin/psql -p %s -d %s -c "CREATE VIEW postgis.uk_borders AS SELECT * FROM postgis.world_borders WHERE fips_cntry = \'UK\'"' % (PGROOT, port, PGDBNAME))
    system('%s/bin/psql -p %s -d %s -c "INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) VALUES (\'\', \'postgis\', \'uk_borders\', \'the_geom\', 2, 4269, \'MULTIPOLYGON\')"' % (PGROOT, port, PGDBNAME))
    system('%s/bin/psql -p %s -d %s -c "CREATE TABLE postgis.us_borders AS SELECT * FROM postgis.world_borders WHERE fips_cntry = \'US\'"' % (PGROOT, port, PGDBNAME))
    system('%s/bin/psql -p %s -d %s -c "INSERT INTO geometry_columns (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type) VALUES (\'\', \'postgis\', \'us_borders\', \'the_geom\', 2, 4269, \'MULTIPOLYGON\')"' % (PGROOT, port, PGDBNAME))

    os.unlink('/tmp/wb.sql')

    if port != '5432':
        # If we're not using the default port, we need to update the
        # test configuration and run the buildout again so that the
        # test runner gets updated.
        open('test-environment.cfg', 'w').write(test_env_tmpl % dict(port=port))
        system('./bin/buildout')

    

def main():
    parser = OptionParser()
    parser.add_option('--port', dest='port', default='5432',
                      help='PostgreSQL server port number')

    options, args = parser.parse_args()

    initpg(port=options.port)

    print '\n\n'
    print 'PostgreSQL test server initialized'
    print '----------------------------------'
    print 'The server is listening on localhost:%s' % options.port
    print 'You can control the server process by using the ./bin/pg_ctl script' 


if __name__ == '__main__':
    main()




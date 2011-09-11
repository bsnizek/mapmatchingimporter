from geoalchemy import Table, GeometryColumn, Geometry, LineString, Point, GeometryDDL, GeometryExtensionColumn, GeometryCollection, DBSpatialElement, WKTSpatialElement, WKBSpatialElement
from geoalchemy.postgis import PGComparator, pg_functions
from osgeo import ogr,osr
from random import random
from sqlalchemy import create_engine, MetaData, Column, Integer, Numeric, String, Boolean, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper

from config import *

class ImportOSM(object):
    """The importer 
    """
    engine = create_engine(POSTGRESQL_CONNECTION_STRING, echo = ECHO)
    metadata = MetaData(engine)
    session = sessionmaker(bind=engine)()
    Base = declarative_base(metadata=metadata)
    
    class Respondent(Base):
        """
        """
        
        __tablename__ = "respondent"
        
        id = Column(Integer, primary_key=True)
        
        def __init__(self):
            """
            """
            pass
        
        def __repr__(self):
                print "<Respondent nummer %d" % rspdid
                
    class SourceRoute(Base):
        
        __tablename__ = "sourceroute"
         
        id = Column(Integer, primary_key=True)
        respondentid = Column(Integer, ForeignKey("respondent.id"))
        
    class SourcePoint(Base):
        """
        """
        
        __tablename__ = "sourcepoint"
        
        id = Column(Integer, primary_key=True)
        the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)
        sourcerouteid = Column(Integer, ForeignKey("sourceroute.id"))
        
    class OsmNode(Base):
        """
        """
        __tablename__ = "osmnode"
        id = Column(Integer, primary_key=True)
        the_geom = GeometryColumn(Geometry(1), comparator=PGComparator, nullable=True)
        
    class OsmEdge(Base):
        """
        """
        __tablename__ = "osmedge"
        id = Column(Integer, primary_key=True)
        the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)
        
    class ResultRoute(Base):
        """
        """
        __tablename__ = "resultroute"
        id = Column(Integer, primary_key=True)
        the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)
        sourcerouteid = Column(Integer, ForeignKey("sourceroute.id"))
        selected = Column(Boolean)
        length = Column(Numeric)
        # ... [TODO] more fields regarding to 
        
    class ResultNodes(Base):
        __tablename__ = "resultnodes"
        id = Column(Integer, primary_key=True)
        resultrouteid = Column(Integer, ForeignKey("resultroute.id"))
        counter = Column(Integer)
        osmnodeid = Column(Integer, ForeignKey("osmnode.id"))
        nearestedge = Column(Integer, ForeignKey("osmedge.id"))
        nearstedgedistance = Column(Numeric)
        
        
    GeometryDDL(SourcePoint.__table__)
    GeometryDDL(OsmNode.__table__)
    GeometryDDL(OsmEdge.__table__)
    GeometryDDL(ResultRoute.__table__)
        
    def createTables(self):
        """
        """
        self.metadata.drop_all()
        self.metadata.create_all()
        
    def importGPSTrackFromShape(self, inFile, index=0):
        """
        """
        self.shapeFile = ogr.Open(inFile)
        if self.shapeFile is None:
            print "Failed to open " + inFile + ".\n"
            sys.exit( 1 )
        else:
            lyrcount = self.shapeFile.GetLayerCount() # multiple layers indicate a directory 
            for lyrindex in xrange(lyrcount):
                lyr = self.shapeFile.GetLayerByIndex(lyrindex)
                flds = [x.GetName() for x in lyr.schema]
                import pdb;pdb.set_trace()
            
            
    
ios = ImportOSM()
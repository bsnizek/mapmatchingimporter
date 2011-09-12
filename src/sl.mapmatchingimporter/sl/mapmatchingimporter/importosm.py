NO_COMPARATOR = False

from geoalchemy import Table, GeometryColumn, Geometry, LineString, Point, GeometryDDL, GeometryExtensionColumn, GeometryCollection, DBSpatialElement, WKTSpatialElement, WKBSpatialElement
try:
    from geoalchemy.postgis import PGComparator
except:
    NO_COMPARATOR=True
from osgeo import ogr,osr
from random import random
from sqlalchemy import create_engine, MetaData, Column, Integer, Numeric, String, Boolean, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper

from config import *

import sys

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
        
        
        def __init__(self, geometry):
            self.the_geom = geometry
        
    class OsmNode(Base):
        """
        """
        __tablename__ = "osmnode"
        id = Column(Integer, primary_key=True)
        the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)

        def __init__(self, geometry):
            self.the_geom = geometry
        
             
    class OsmEdge(Base):
        """
        """
        __tablename__ = "osmedge"
        id = Column(Integer, primary_key=True)
        the_geom = GeometryColumn(Geometry(2), comparator=PGComparator, nullable=True)
            
        def __init__(self, geometry):
            self.the_geom = geometry
            
        
    class ResultRoute(Base):
        """
        """
        __tablename__ = "resultroute"
        id = Column(Integer, primary_key=True)
        if NO_COMPARATOR:
            the_geom = GeometryColumn(Geometry(2), nullable=True)
        else:
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
        
    def getfieldinfo(self, lyr, feature, flds):
            f = feature
            return [f.GetField(f.GetFieldIndex(x)) for x in flds]
        
    def importGPSTrackFromShape(self, inFile):
        """
        """
        shapeFile = ogr.Open(inFile)
        if shapeFile is None:
            print "Failed to open " + inFile + ".\n"
            sys.exit( 1 )
        else:
            lyrcount = shapeFile.GetLayerCount() # multiple layers indicate a directory 
            for lyrindex in xrange(lyrcount):
                lyr = shapeFile.GetLayerByIndex(lyrindex)
                fields = [x.GetName() for x in lyr.schema]
                for findex in xrange(lyr.GetFeatureCount()):
                    f = lyr.GetFeature(findex)
                    flddata = self.getfieldinfo(lyr, f, fields)
                    coord = f.GetGeometryRef().GetPoint()
                    # attributes = dict(zip(fields, flddata))
                    # import pdb;pdb.set_trace()
                    
                    
                    pt = ogr.Geometry(ogr.wkbPoint)
                    pt.SetPoint_2D(0, coord[0], coord[1])

                    feat = ogr.Feature( lyr.GetLayerDefn())
                    feat.SetGeometryDirectly(pt)
                    
                    # import pdb;pdb.set_trace()
                    sourcepoint = self.SourcePoint(feat.GetGeometryRef().ExportToWkt())
                    self.session.add(sourcepoint)
                    
            self.session.commit()
            print "GPS Track loaded into database."
        
    def importRoadNetwork(self, inFile):
        """
        """
        shapeFile = ogr.Open(inFile)
        if shapeFile is None:
            print "Failed to open " + inFile + ".\n"
            sys.exit( 1 )
        else:
            lyrcount = shapeFile.GetLayerCount() # multiple layers indicate a directory 
            for lyrindex in xrange(lyrcount):
                lyr = shapeFile.GetLayerByIndex(lyrindex)
                fields = [x.GetName() for x in lyr.schema]
                for findex in xrange(lyr.GetFeatureCount()):
                    f = lyr.GetFeature(findex)
                    flddata = self.getfieldinfo(lyr, f, fields)
                    geometry = f.GetGeometryRef()
                    osmedge = self.OsmEdge(geometry.ExportToWkt())
                    self.session.add(osmedge)
            self.session.commit()
            print "OSM Edges loaded into database."
        
            
    
ios = ImportOSM()
ios.createTables()
ios.importGPSTrackFromShape("/Users/besn/git/mapmatchingimporter/testdata")
ios.importRoadNetwork("/Users/besn/git/mapmatchingimporter/testdata/Sparse_bigger0.shp")
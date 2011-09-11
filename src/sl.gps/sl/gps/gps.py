""" bikeability.dk
    
    (c) 2011 Snizek & Skov-Petersen
    bikeability@life.ku.dk
    http://www.bikeability.dk
    
    License : GPL

    Created on May 9, 2011

    @author: Bernhard Snizek <besn@life.ku.dk>
    @author: Pimin Kostas Kefaloukos
    @author: Hans Skov-Petersen <hsp@life.ku.dk>

    These modules are part of Bikeability.dk.

    Read more about Bikeability her: http://www.bikeability.dk

    Please refer to INSTALL for correct installation as well as information on 
    dependencies etc. 
"""

from pygpx import GPXTrackPt, GPXTrack, GPXTrackSeg, datetime_iso
import sys
from xml.dom.minidom import parse
try:
    from osgeo import ogr
except ImportError:
    raise ImportError("read_shp() requires OGR: http://www.gdal.org/")

import shapely.wkt
from shapely.geometry import Point

class NodeSurrogate:
    
    childNodes = []
    
    def __init__(self):
    
        self.nodeName = "xxx"
        self.childNodes = []
    
    

class GPSTrack(GPXTrack):
    """A GPS track with some modification
    
    """
    def __init__(self, node, version):
        """Create a GPX track, give an XML DOM node and the document version."""
        
        self.version = version
        self.trksegs = []
        
        for node in node.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            if node.nodeName == "name":
                self.name = node.firstChild.data                
            elif node.nodeName == "trkseg":
                self.trksegs.append(GPSTrackSegment(node, self.version))
            elif node.nodeName == "number":
                self.name = node.firstChild.data                
            else:
                raise ValueError, "Bugger. can't handle node <%s>" % node.nodeName
        
    def getName(self):
        return self.name
    
    def addGPSTrackSegment(self, seg):
        self.trksegs.append(seg)


class GPSTrackSegment(GPXTrackSeg):
    """A track segment with slight modifications.
    """
    
    def __init__(self, node, version):
        self.version = version
        self.trkpts = []
        for node in node.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            elif node.nodeName == "trkpt":
                self.trkpts.append(GPSTrackPoint(node, self.version))
            else:
                raise ValueError, "Can't handle node <%s>" % node.nodeName
        
    def getPoints(self):
        return self.trkpts
    
    def addGPSTrackPoint(self, point):
        self.trkpts.append(point)


class GPSTrackPoint(GPXTrackPt):
    """A GPS point with a slight modficiation
    """
    def __init__(self, node, version, geometry=None, attributes={}):
        """Construct a trackpint given an XML node."""

        self.version = version
        self.attributes = {}
        
        if geometry:
            self.geometry = geometry
            self.attributes = attributes
            self.version = u"1.0"
        else:

            self.lat = float(node.getAttribute("lat"))
            self.lon = float(node.getAttribute("lon"))
            
            self.elevation = None
            self.time = None
            for node in node.childNodes:
                if node.nodeType != node.ELEMENT_NODE:
                    continue
                if node.nodeName == "time":
                    self.time = datetime_iso(node.firstChild.data)
                    self.attributes['time'] = self.time
                elif node.nodeName == "ele":
                    self.elevation = float(node.firstChild.data)
                else:
                    raise ValueError, "Can't handle node", node.nodeName

            if self.elevation:
                self.geometry   = Point(
                                  float(self.lat),
                                  float(self.lon),
                                  float(self.elevation)
                                  )
            else:
                self.geometry   = Point(
                                  float(self.lat),
                                  float(self.lon)
                                  )
            
    def getPoint(self):
        return self.geometry
    
    def getAttributes(self):
        """Returns the attributes of this TrackPoint
        """
        return self.attributes
    
    def getGeometry(self):
        """Returns the geometry of this GPSTrackPoint as a Shapely Point object.
        """
        return self.geometry
    
    def getGeometry2D(self):
        """Returns the geometry as a 
        """
        return Point(self.geometry.x, self.geometry.y)

class GPS:
    
    def __init__(self):
        """"""
        self.creator = None
        self.time = None
        self.tracks = []
        self.trackname__track = {}

    def _init_version_1_0(self):
        """Initialise a version 1.0 GPX instance."""
        self.creator = self.gpx_hdr.getAttribute("creator")
        for node in self.gpx_hdr.childNodes:
            if node.nodeType != node.ELEMENT_NODE:
                continue
            if node.nodeName == "time":
                self.time = node.firstChild.data
            elif node.nodeName == "trk":
                trk = GPSTrack(node, self.version)
                self.tracks.append(trk)
                self.trackname__track[trk.getName()] = trk 
            else:
                raise ValueError, "Bugger, I cannot handle node !", node.nodeName
            
    def getfieldinfo(self, lyr, feature, flds):
            f = feature
            return [f.GetField(f.GetFieldIndex(x)) for x in flds]

    
    def readFromShapeFile(self, inFile):
        """Reads GPS data from a ESRI Shapefile.
        """
        

        self.creator = "Generated from a Shaopefile."
        
        self.gpsFile = ogr.Open(inFile)
        if self.gpsFile is None:
            print "Failed to open " + inFile + ".\n" 
            sys.exit( 1 )
        else:
            
            track = GPSTrack(NodeSurrogate, "1.0")
            trackseg =GPSTrackSegment(NodeSurrogate, "1.0")
            
            self.shapelyGPS = self.gpsFile.GetLayer(0)
            
            lyrcount = self.gpsFile.GetLayerCount()
            
            for lyrindex in xrange(lyrcount):
                lyr = self.gpsFile.GetLayerByIndex(lyrindex)
                flds = [x.GetName() for x in lyr.schema]
            
                
            for i in range(self.shapelyGPS.GetFeatureCount()):
                feature = self.shapelyGPS.GetFeature(i)
                geometry = feature.GetGeometryRef()
                
                flddata = self.getfieldinfo(lyr, feature, flds)
                attributes = dict(zip(flds, flddata))
                

                p = GPSTrackPoint(None,
                                  "1.0",
                                  geometry=shapely.wkt.loads(geometry.ExportToWkt()), 
                                  attributes=attributes )
                
                
                trackseg.addGPSTrackPoint(p)
            track.addGPSTrackSegment(trackseg)
            self.tracks.append(track)
            self.trackname__track["dummy"] = track
                
            print "GPS file successfully read"
                
    
    def readFromGPXFile(self, filename):
        """
        """
        self.dom = parse(filename)
        self.gpx_hdr = self.dom.firstChild
        self.version = self.gpx_hdr.getAttribute("version")
        if self.version == "1.0":
            self._init_version_1_0()
        else:
            raise ValueError, "Can't handle version", self.version
    
    def distance(self):
        """Returns the total distance for the GPS track
        """
        dist = 0
        for trk in gpx.tracks:
            dist = dist + trk.distance() / 1000.0, trk.duration(), \
                   trk.full_duration(), trk.start_time(), trk.end_time()
        return dist
    
    def getGPSPoints(self, track_name=None):
        """Returns the dataset as a list of GPSPoints. if track is set to None and
        the dataset contains more than 1 track this method will return the
        data is if it were one dataset, capisce ? 
        """
        if track_name:
            track = self.trackname__track.get(track_name,None)
            if track:
                points = []
                for trkseg in track.trksegs:
                    points = points + trkseg.getPoints()
                return points
            else:
                return []    
        else:
            points = []
            for track in self.tracks:
                for trackseg in track.trksegs:
                    points = points + trackseg.getPoints()
            return points
        
if __name__ == '__main__':
    
    gpx = GPS()
    print gpx
    
    # gpx.readFromGPXFile("/Users/bsnizek/pymapmatching2/testdata/nztrip-tracks.gpx")
    gpx.readFromShapeFile("/Users/bsnizek/pymapmatching2/testdata/GPS_Points.shp")
    
    points = gpx.getGPSPoints()
    
    print points[0].getAttributes()
    
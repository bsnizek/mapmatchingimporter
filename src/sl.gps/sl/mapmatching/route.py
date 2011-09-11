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
from osgeo import ogr #@UnresolvedImport

class Route:
    
    def __init__(self, edges=[]):
        self.edges = edges
        
    def getLength(self):
        l = 0
        for edge in self.edges:
            l = l+ edge.getLength()
        return l
    
    def getEdges(self):
        return self.edges
    
    def saveAsShapeFile(self, filename=None):
        """Saves the route as a an ESRIShapefile
        """
        if filename:
            driverName = "ESRI Shapefile"
            drv = ogr.GetDriverByName( driverName )
            
            if drv:
                drv.DeleteDataSource(filename)
        
            if drv is None:
                print "%s driver not available.\n" % driverName    
            ds = drv.CreateDataSource( filename)
            
            lyr = ds.CreateLayer( "blabla", None, ogr.wkbLineString )
            if lyr is None:
                print "Layer creation failed.\n"
            
            for edge in self.getEdges():
                feat = ogr.Feature( feature_def=lyr.GetLayerDefn())
                line = ogr.Geometry(type=ogr.wkbLineString)
#                wkb = edge.getGeometry().to_wkb()
                for coord in edge.getGeometry().coords:
                    line.AddPoint_2D(coord[0],coord[1])
                feat.SetGeometryDirectly(line)
                lyr.CreateFeature(feat)
                feat.Destroy()
            
            print "Route written."
            
        
    
    
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

class Label:
    """The label for the labelling algorithm
    """
    
    def __init__(self, node, parent=None, back_edge=None, length=1):
        self.node = node
        self.parent = parent
        self.back_edge = back_edge
        self.length = length
        print "Label at " + str(node.getAttributes()) + " instantiated"
        
    def getParent(self):
        """Returns the parent label
        """
        return self.parent
    
    def getNode(self):
        """Returns the current node
        """
        return self.node
    
    def getAttributes(self):
        return self.getNode().getAttributes()
    
    def getBackEdge(self):
        """Returns the edge that points backwards in the label hierarchy.
        """
        return self.back_edge
    
    def getLength(self):
        """Returns the length of the node (in real world units)
        """
        return self.length
    
    def getOccurancesOfEdge(self, edge):
        """Returns the occurance of an edge in relation to the edge hierarchy
        """
        label = self
        result = 0
        while (label.getBackEdge() != None ):
            backedge = label.getBackEdge()
            if (edge == backedge):
                result = result + 1
            label = label.getParent()
            
        return result
    
    def getOccurancesOfNode(self, node):
        """Returns the number of occurences of <node> as an integer
        """
        label = self
        result = 0
        while (label != None):
            if node.getAttributes().get("nodecounter") == label.getNode().getAttributes().get("nodecounter"):
                result = result + 1
            label = label.getParent()
                
#            result.append(label.getBackEdge())
#            label = label.getParent()
            
#        result.reverse()
        return result
    
    def getRouteLabels(self):
        """Returns the route as labels
        """
        labels = []
        currlabel = self
        # labels.append(self)
        
        while currlabel:
           #  print currlabel.getAttributes()
            currlabel = currlabel.getParent()
            labels.append(currlabel)

        return  [self] + labels
    
    def getEdges(self):
        """Returns a list of edges in forward order.
        """
        edges = [label.getBackEdge() for label in self.getRouteLabels() if label]
        edges = [edge for edge in edges if edge]
        edges.reverse()
        return edges
    
    def getRouteAttributes(self):
        """Returns a list of edge attributes in forward order.
        """
        return [edge.getAttributes() for edge in self.getEdges()] 
    
    def printRouteAttributes(self):
        print [edge.getAttributes() for edge in self.getEdges()] 
        
        
    def saveAsShapeFile(self, filename=None):
        """Saves the route as a an ESRIShapefile
        """
        if filename:
            driverName = "ESRI Shapefile"
            drv = ogr.GetDriverByName( driverName )
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
                
    def saveAsShapeFile2(self, base=None):
        """Saves the route as a an ESRIShapefile
        """
        if base:
            driverName = "ESRI Shapefile"
            drv = ogr.GetDriverByName( driverName )
            drv.DeleteDataSource(base + str(self.getNode().getAttributes().get("nodecounter")) + ".shp")
        
            if drv is None:
                print "%s driver not available.\n" % driverName    
            
            ds = drv.CreateDataSource( base + str(self.getNode().getAttributes().get("nodecounter")) + ".shp")
            
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
                
            import pdb;pdb.set_trace()
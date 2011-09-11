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
    
    def __init__(self, node, parentLabel=None, parentEdge=None, endNode = None, routeFinder = None, length=0, star=None):
        self.node = node
        self.parentLabel = parentLabel
        self.parentEdge = parentEdge
        self.star = star
        self.endNode = endNode
        self.routeFinder = routeFinder
        self.length = length
        # print "Label() at " + str(node.getAttributes().get("nodecounter"))
        # self.printRouteLabels()
        
        
    def removeEdgeFromStar(self, edge):
        self.star.remove(edge)
        
    def checkValidity(self, parentLabel):
        """Returns 
        
            0 
            
            1 everything is OK and we are on the way
            
            2 if the label already in the upward list
            
            3 if the length of the upward distance is > then the MAX LENGTH
              defined in the route finder
              
            4 if the euclidean distance exceeds the max length
                 
        """

        if self.getNode().getAttributes().get("nodecounter") == self.endNode.getAttributes().get("nodecounter"):
            # destination reached
            return 0

        if self.getLength() > self.routeFinder.getMaxLength():
            return 3
        
        if (self.routeFinder.getMaxLength() - self.getLength()) < self.routeFinder.euclideanOD[self.getNode()][self.endNode]:
            return 4
        

        if self.getOccurancesOfNode(self.getNode())>1:
            # node already in upwards label list 
            return 2
        else: 
            # still on the way
            return 1
        
            
    def getBackEdge(self):
        """Returns the edge that points backwards in the label hierarchy.
        """
        return self.parentEdge
            
        
    def getStar(self):
        return self.star
        
        
    def getParent(self):
        """Returns the parent label
        """
        return self.parentLabel
    
    def getNode(self):
        """Returns the current node
        """
        return self.node
    
    def getAttributes(self):
        return self.getNode().getAttributes()
    

    
    def getLength(self):
        """Returns the length of the node (in real world units)
        """
        l = 0
        for e in self.getEdges():
            l = l + e.getLength()
        
        return l
    
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
    
    def printRouteLabels(self):
        s = str(self.getNode().getAttributes().get("nodecounter"))  +  " : "
        l = self.getRouteLabels()
        l.reverse()
        for r in l:
            if r:
                s = s + str(r.getNode().getAttributes().get("nodecounter")) + "-"
        return s 
    
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
            
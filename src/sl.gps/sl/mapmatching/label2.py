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
    
    def __init__(self, node, parentLabel=None, parentEdge=None, endNode = None, routeFinder = None, length=0):
        self.node = node
        self.parentLabel = parentLabel
        self.parentEdge = parentEdge
        self.star = node.getOutEdges()
        self.endNode = endNode
        self.routeFinder = routeFinder
        self.length = length
        print "Label() at " + str(node.getAttributes().get("nodecounter"))
#        if parentLabel:
#            print "parentLabel ", parentLabel.getAttributes().get("nodecounter")
            
        # import pdb;pdb.set_trace()
        
    def expand(self, maxDist=0, minDist=0, endNode=None):
        """Expands the node
        """
        
        # print "Starting to expand ", self.getNode().getAttributes().get("nodecounter") 
        
        self.edges = self.getStar()
 
        while len(self.edges) > 0:
            print "."
            edge = self.edges.pop()
            
            # print "instantiating to outnode ", edge.getOutNode(self).getAttributes().get("nodecounter")
            
            # import pdb;pdb.set_trace()
            if self.parentLabel:
                length = self.parentLabel.getLength() + edge.getLength()
            else:
                length = edge.getLength()
            
            currentLabel = Label(edge.getOutNode(self), 
                                 parentLabel = self, 
                                 parentEdge=edge, 
                                 endNode=self.endNode, 
                                 routeFinder=self.routeFinder, 
                                 length=length)
            
            check = currentLabel.checkValidity(edge.getOutNode(self), self)
            
            # print check
            
            if check == 0:
                
                print "route found" 
                self.routeFinder.results.append(self)
                # self.saveAsShapeFile('Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/x' + str(len(self.routeFinder.results)) + '.shp' )
                
            
            if check == 2:
                pass
            
            if check == 1:
                currentLabel.expand(maxDist=0, minDist=0, endNode=self.endNode)
        
        
                
    def checkValidity(self, node, parentNode):
        if self.getNode() == self.endNode:
            return 0

        if self.getOccurancesOfNode(parentNode)>1:
            # print "parent Node occurance."
            return 2
        else:
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
            
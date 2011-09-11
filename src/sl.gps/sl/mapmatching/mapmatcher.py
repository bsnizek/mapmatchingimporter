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

import networkx as nx
from utils import GraphToShape
from sl.gps.gps import GPS
try:
    from osgeo import ogr
except ImportError:
    raise ImportError("read_shp() requires OGR: http://www.gdal.org/")
import sys
from routefinder import RouteFinder
from rtree import Rtree
import shapely.wkt
from shapely.geometry import Point

from route import Route 

INTERSECTION_MASK = 0.5

# BASE_PATH = "/Users/hansskov-petersen/pymapmatching/src/sl/mapmatching/testdata/"
BASE_PATH = "/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/"



class Edge:
    """A nifte edge class for our graph.
    """
    
    def __init__(self, point2D_from, point2D_to, attributes=None, geometry=None):
        """The nice constructor
        """
        self.from_node = point2D_from
        self.to_node = point2D_to
        self.attributes = attributes
        self.geometry = geometry
        
        sfx1 = self.from_node.getPoint()[0]
        sfx2 = self.to_node.getPoint()[0]
        if sfx1 > sfx2:
            self.minx = sfx2
            self.maxx = sfx1
        else:
            self.minx = sfx1
            self.maxx = sfx2
        sfy1 = self.from_node.getPoint()[1]
        sfy2 = self.to_node.getPoint()[1]
        if sfy1 > sfy2:
            self.miny = sfy2
            self.maxy = sfy1
        else:
            self.miny = sfy1
            self.maxy = sfy2
        
    def getAttributes(self):
        """Returns our attributes as a dict
        """
        return self.attributes
        
    def getMinX(self):
        """Returns the minimum latitude.
        """
        return self.minx
    
    def getMaxX(self):
        """Returns the maximum latitude.
        """
        return self.maxx
    
    def getMinY(self):
        """Returns the minimum longitude
        """
        return self.miny
    
    def getMaxY(self):
        """Returns the maximum longitude
        """
        return self.maxy
    
    def getLength(self):
        """Returns the length of the edge (takes vertices into consideration)
        """
        return self.geometry.length
    
    def getToNode(self):
        """Returns the to/target node of the edge.
        """
        return self.to_node

    def getFromNode(self):
        """Returns the to/target node of the edge.
        """
        return self.from_node
   
    def getGeometry(self):
        """Returns the edges geometry as a Shapely Multipoint object
        """
        return self.geometry
    
    def setAttributes(self, attributes):
        """Sets attributes (dict)
        """
        self.attributes = attributes
        
    def getOutNode(self, label):
        to_counter = self.getToNode().getAttributes().get("nodecounter")
        from_counter = self.getFromNode().getAttributes().get("nodecounter")
        label_counter = label.getNode().getAttributes().get("nodecounter")
        
        if label_counter == to_counter:
            return self.getFromNode()
        else:
            return self.getToNode()

    def getOutNode2(self, node):
        to_counter = self.getToNode().getAttributes().get("nodecounter")
        from_counter = self.getFromNode().getAttributes().get("nodecounter")
        label_counter = node.getAttributes().get("nodecounter")
        
        if label_counter == to_counter:
            return self.getFromNode()
        else:
            return self.getToNode()        
        
class Node:
    
    def __init__(self, point, attributes=None):
        
        self.point = point
        self.attributes = attributes
        self.geometry = Point(point[0], point[1])
         
    def getOutEdges(self):
        """Returns the star of Edges from this node
        """
        edges = []
        
        for edict in mm.G[self].values():
            for k in edict.keys():
                edges.append(edict.get(k).get("edge"))
        
        return edges
    
    def getPoint(self):
        """Returns the geometry. compatibility method; see getGeometry()
        """
        return self.point
    
    def getAttributes(self):
        """Returns the attributes as a dict.
        """
        return self.attributes
    
    def getGeometry(self):
        """Returns the geometry (Shapely Point) of this node.
        """
        return self.geometry
    
    def getNodeID(self):
        return self.getAttributes().get('nodecounter')
        


class MapMatcher():
    """A very nice MapMatching class
    """
    
    def __init__(self):
        self.GPS = GPS()
        self.idx = Rtree()
        self.nodeidx = Rtree()
        self.G = None
        self.edgeindex_edge = {}
        self.edgecounter = 0
        self.nodecounter = 0
        self.gps_points = [];
        self.edge_id__count = {}
        self.node_counter__node = {}
        self.distance_matrix = {}
        
    def saveGraph(self, filename):
        """Saves the graph as a YAML file
        """
        nx.write_yaml(self.G,filename)
        
    def readGraphFromYAMLFile(self, filename):
        """Loads a graph from an YAML file. 
        """
        self.G = nx.read_yaml(filename)
        # TODO: buiild up the indexes !!!
        
        
    def addNodeToIndex(self, node):
        """Adds a node to the node index (RTree)
        """
        # self.nodeidx.add(self.nodecounter, (node.getPoint()[0], node.getPoint()[1]), obj=node)
        self.nodeidx.add(self.nodecounter, (node.getPoint()[0], node.getPoint()[1], node.getPoint()[0], node.getPoint()[1]))

        self.node_counter__node[self.nodecounter] = node
        
    
    def addEdgeToIndex(self, edge): 
        """Add an edge to the edhe index.
        """
        self.idx.add(self.edgecounter, (edge.getMinX(), edge.getMinY(), edge.getMaxX(), edge.getMaxY()),obj=edge)
        # print "%d/%d -> %d/%d" % (edge.getMinX(), edge.getMinY(), edge.getMaxX(), edge.getMaxY())
        self.edgeindex_edge[self.edgecounter] = edge
        self.edgecounter = self.edgecounter + 1
        
    def openShape(self, inFile, index=0):
        self.shapeFile = ogr.Open(inFile)
        if self.shapeFile is None:
            print "Failed to open " + inFile + ".\n"
            sys.exit( 1 )
        else:
            print "SHP file successfully read"
     
    def getfieldinfo(self, lyr, feature, flds):
            f = feature
            return [f.GetField(f.GetFieldIndex(x)) for x in flds]
     
    def addlyr(self, G,lyr, fields):
        
        point_coords__nodes = {}
        
        for findex in xrange(lyr.GetFeatureCount()):
            f = lyr.GetFeature(findex)
            flddata = self.getfieldinfo(lyr, f, fields)
            g = f.geometry()
            attributes = dict(zip(fields, flddata))
            attributes["ShpName"] = lyr.GetName()
            
            if g.GetGeometryType() == 2: #linestring
                last = g.GetPointCount() - 1
                p_from = g.GetPoint_2D(0)
                p_to = g.GetPoint_2D(last)
                 
                 # check whether we have a node in the index
                
                intersection_mask = (p_from[0]-INTERSECTION_MASK/2, 
                                     p_from[1]-INTERSECTION_MASK/2,
                                     p_from[0]+INTERSECTION_MASK/2, 
                                     p_from[1]+INTERSECTION_MASK/2)
                
                results = list(self.nodeidx.intersection(intersection_mask))
                
                if len(results)==0:
                    
                    #print "New from-node " + str(self.nodecounter) + " for edge " + str(attributes.get("ID_NR")) + "."
                    
                    
                    pfrom = Node(p_from, attributes={'from_edge':attributes.get(self.shapeFileUniqueId), "nodecounter":self.nodecounter})
                    self.node_counter__node[self.nodecounter] = pfrom
                    self.nodeidx.add(self.nodecounter, (p_from[0], 
                                                        p_from[1], 
                                                        p_from[0], 
                                                        p_from[1]))
                    # print p_from
                    self.nodecounter = self.nodecounter + 1
                else:
                    #print len(results)
                    #print "From-node " + str(results[0]) + " recycled for edge " + str(attributes.get("ID_NR")) + "."
                    
                    pfrom = self.node_counter__node[results[0]]
                    

                intersection_mask = (p_to[0]-INTERSECTION_MASK/2, 
                                     p_to[1]-INTERSECTION_MASK/2,
                                     p_to[0]+INTERSECTION_MASK/2, 
                                     p_to[1]+INTERSECTION_MASK/2)
                
                # print intersection_mask
                
                results = list(self.nodeidx.intersection(intersection_mask))

                if len(results)==0:
                    
                    #print "New to-node " + str(self.nodecounter) + " for edge " + str(attributes.get("ID_NR")) + "."
                    
                    pto = Node(p_to, attributes={'to_edge':attributes.get(self.shapeFileUniqueId), "nodecounter":self.nodecounter})
                    self.node_counter__node[self.nodecounter] = pto
                    self.nodeidx.add(self.nodecounter, (p_to[0], 
                                                        p_to[1], 
                                                        p_to[0], 
                                                        p_to[1]))
                    self.nodecounter = self.nodecounter + 1
                else:
                    
                    #print "To-node " + str(results[0]) +  " recycled for edge " + str(attributes.get("ID_NR")) + "."
                    
                    pto = self.node_counter__node[results[0]]
                    
                    
                shly_geom = shapely.wkt.loads(g.ExportToWkt())
                
                e = Edge(pfrom, pto, attributes, geometry = shly_geom)
                
                # G.add_edge(pfrom, pto, {"edge": e, "edgecounter" : self.edgecounter})
                
                G.add_edge(pfrom, pto, edge=e, edgecounter=self.edgecounter)
                
                self.addEdgeToIndex(e)     
                
        return G
            
    def shapeToGraph(self, inFile, uniqueId="FID"):
        """Loads a shapefile and builds the graph.
        uniqueId is the name of a unique field in the shape file. 
        """
        # self.G = nx.readwrite.nx_shp.read_shp(inFile)
        
        self.G = nx.MultiGraph()
        
        self.shapeFileUniqueId = uniqueId
        
        lyrcount = self.shapeFile.GetLayerCount() # multiple layers indicate a directory 
        for lyrindex in xrange(lyrcount):
            lyr = self.shapeFile.GetLayerByIndex(lyrindex)
            flds = [x.GetName() for x in lyr.schema]
            self.G=self.addlyr(self.G, lyr, flds)
            
        self.routefinder = RouteFinder(self.G, euclideanOD=self.distance_matrix)

    def readGPS(self, inFile):
        """Parses a shapefile and build the GPS object
        """
        self.GPS.readFromShapeFile(inFile)
        self.gps_points = self.GPS.getGPSPoints()
                
    def maxGPSDistance(self):
        """Calculate the maximum distance of two consecutive GPS Points
        """
        # TODO check whether GPS points are already there
        # TODO: move into sl.gps.GPS()
        maxDistance = 0
        gps_point = self.gps_points[0]
        for gpspoint in self.gps_points:
            distance = gpspoint.getGeometry().distance(gps_point.getGeometry())
            gps_point = gps_point
            
            if distance > maxDistance:
                maxDistance = distance
                
        return maxDistance
        

    def nearPoints(self):
        """Sums up the gps point per edge segment. Stores in self.edge_id__count
        """
        # initialize the edge counter
        for edge in self.G.edges():
            self.edge_id__count[self.G[edge[0]][edge[1]].get("edgecounter")] = 0
    
        for point in self.gps_points:
            nearest_edge = self.getNearestEdge(point)
            # print str(point.getAttributes().get("ID")) + "->" + str(nearest_edge.getAttributes().get('Id'))
            self.addPointCountToEdge(nearest_edge)
            
    def addPointCountToEdge(self, edge):
        """Increments the point counter for the given edge by one.
        """
        attributes = edge.getAttributes()
        if self.edge_id__count.has_key(attributes.get(self.shapeFileUniqueId)):
            self.edge_id__count[attributes.get(self.shapeFileUniqueId)] = self.edge_id__count[attributes.get(self.shapeFileUniqueId)] + 1
        else:
            self.edge_id__count[attributes.get(self.shapeFileUniqueId)] = 1
        edge.setAttributes(attributes)
    
    def getNearestEdge(self, point):
        """Returns the edge closes to a Shapely entity given (point) 
        """
        edge = mm.idx.nearest((point.getPoint().x, point.getPoint().y), objects=True)
        edges = [e.object for e in edge]
        if len(edges) == 1:
            result = edges[0]
        else:
            dist = 99999999999999999999999999999999999999999
            for edge in edges:
                distance = point.getPoint().distance(edge.getGeometry())
                if distance < dist:
                    dist = distance
                    result = edge
        return result
    
    
    def getNearestNode(self, point):
        """Returns the closest node to a GPS point.
        """
        nodes = list(mm.nodeidx.nearest((point.getPoint().x, point.getPoint().y)))
        return self.node_counter__node.get(nodes[0])
    
    def find_all_paths(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not graph.has_key(start):
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = self.find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths 
    
    def findRoutes2(self):
        
        start_point = self.gps_points[0]
        end_point = self.gps_points[-1]
        
        start_node =  self.getNearestNode(start_point)
        end_node =  self.getNearestNode(end_point)
        
        graph = {}
        print "preparing python graph"
        
        for node in  self.node_counter__node.values():
            graph[node.getNodeID()] =  [n.getOutNode2(node).getNodeID() for n in node.getOutEdges()]
        
        import pprint
        pprint.pprint( graph )
        
        print "From ", start_node.getNodeID(), " to ", end_node.getNodeID(), "."
        results = self.find_all_paths(graph, start_node.getNodeID(), end_node.getNodeID())
            
        # let us find the edges
        route_list = []    
        for result in results:
            i=1
            edges = []
            while i<len(result):
                node_from = self.node_counter__node.get(result[i-1] )
                node_to = self.node_counter__node.get(result[i] )
                i = i +1
                edge_dict = self.G[node_from][node_to]
                if edge_dict.keys()>1:
                    lngth = 9E99999
                    
                    for k in edge_dict.keys():
                        
                        if edge_dict[k]['edge'].getLength() < lngth:
                            lngth = edge_dict[k]['edge'].getLength()
                            edge = edge_dict[k]['edge']
                else:
                    edge = edge_dict[0]['edge']
                
                edges.append(edge)
           
            route_list.append(Route(edges))
           
        factor__selected_route = {}
         
        for route in route_list:
            
            number_of_points = 0
            length = 0 
            for edge in route.getEdges():
                
                # import pdb;pdb.set_trace()
                
                length = length + edge.getLength()
                
                edge_id = edge.getAttributes().get(self.shapeFileUniqueId)
                
                number_of_points = number_of_points + self.edge_id__count.get(edge_id, 0)
                
            if number_of_points > 1:
                
                factor__selected_route[number_of_points/length] = route
                
        keys = factor__selected_route.keys()
        keys.sort()
        
        return factor__selected_route.get(keys[0])
        
        
    def findRoute(self, returnNonSelection=False):
        """Finds a route from the node closest to the first GPS point to 
        the node closest to the latest GPS point. 
        """
        
        # pick the start and end GPS points # TODO: sort GPS Points first
        start_point = self.gps_points[0]
        end_point = self.gps_points[-1]
        
        start_node =  self.getNearestNode(start_point)
        end_node =  self.getNearestNode(end_point)
        
        # the start and endnodes returns by the index are not in the graph, 
        # therefore we need to look them up ....
        
        start_node = self.node_counter__node.get(start_node.getAttributes().get("nodecounter"))
        end_node = self.node_counter__node.get(end_node.getAttributes().get("nodecounter"))
        
        self.routfinder = RouteFinder(self.G, euclideanOD=self.distance_matrix)
        label_list = self.routefinder.findroutes(start_node, end_node)

        label_scores = []
        
        # import pdb;pdb.set_trace()
        
        # let us loop through the label list 
        for label in label_list:
            number_of_points = 0
            # we sum up the number of points and relate them to the length of the route
            print label
            
            for edge in label.getEdges():

                edge_id = edge.getAttributes().get(self.shapeFileUniqueId)
                number_of_points = number_of_points + self.edge_id__count.get(edge_id, 0)
                print "      ", number_of_points
            #we add the scores to a dict
            
            if number_of_points > 1:
                label_scores.append((label, number_of_points/label.getLength()))
            
        # print label_scores
        
        # and extract the maximum score
        score = 0
        selected = None
        
        for ls in label_scores:
            if ls[1] > score:
                selected = ls[0]
                score = ls[1]
        
        if returnNonSelection:
            pass
        else:
            return selected
        
    def eliminiateEmptyEdges(self, distance = 100):
        """Loops through the GPS pointset and selects edges within a boundary 
        of <distance> meters
        """
        print "Edge elimination started"
        
        selected_edge_ids = []
        # let us 
        
        for point in self.gps_points:
            results = self.idx.nearest(((point.getPoint().x-distance/2), 
                                     (point.getPoint().y-distance/2),
                                     (point.getPoint().x+distance/2),
                                     (point.getPoint().y+distance/2)), objects=True)
            for result in results:
                from_node = self.node_counter__node.get(result.object.from_node.getAttributes().get("nodecounter"))
                to_node = self.node_counter__node.get(result.object.to_node.getAttributes().get("nodecounter"))
                edge_counter = self.G.edge[from_node][to_node].get("edgecounter")
                if edge_counter not in selected_edge_ids:
                    selected_edge_ids.append(edge_counter)
        print str(len(selected_edge_ids)) + " edges found to keep."
        
        elimination_counter = 0
        for edge in self.G.edges():
            edgecounter = self.G.edge[edge[0]][edge[1]].get("edgecounter")
            if edgecounter not in selected_edge_ids:
                edge_tuple = (self.G.edge[edge[0]][edge[1]].get("edge").from_node, self.G.edge[edge[0]][edge[1]].get("edge").to_node)
                self.G.remove_edge(*edge_tuple)
                elimination_counter =  elimination_counter + 1
          
        print str(elimination_counter) + " edges eliminated."
        
    def dumpPointShape(self, filename, original_coverage=None):
        if filename:
            driverName = "ESRI Shapefile"
            drv = ogr.GetDriverByName( driverName )
            
            if drv:
                drv.DeleteDataSource(filename)
        
            if drv is None:
                print "%s driver not available.\n" % driverName    
            ds = drv.CreateDataSource( filename)
            
            lyr = ds.CreateLayer( "blabla", None, ogr.wkbPoint )
            if lyr is None:
                print "Layer creation failed.\n"

            field_defn = ogr.FieldDefn( "node_count", ogr.OFTInteger )
            
            if lyr.CreateField ( field_defn ) != 0:
                print "Creating Name field failed.\n"
                sys.exit( 1 )    
                
            field_defn = ogr.FieldDefn( "edge_list", ogr.OFTString )
            field_defn.SetWidth( 1024)
            
            if lyr.CreateField ( field_defn ) != 0:
                print "Creating Name field failed.\n"
                sys.exit( 1 )
            
            for node in self.node_counter__node.values():
                
                
                
                feat = ogr.Feature( lyr.GetLayerDefn() )
                
                nc = node.getAttributes().get("nodecounter")
                print nc
                # import pdb;pdb.set_trace()
                feat.SetField( "node_count", nc )  
                s = ""
                for edge in node.getOutEdges():
                    s = s + str(int(edge.getAttributes().get("ID_NR"))) + ", "
                     
                feat.SetField( "edge_list", s )  
                node_entity = ogr.Geometry(ogr.wkbPoint)
#                wkb = edge.getGeometry().to_wkb()
                node_entity.SetPoint_2D(0,node.getGeometry().x, node.getGeometry().y)
                
                feat.SetGeometry(node_entity)
                
                lyr.CreateFeature(feat)
                feat.Destroy()
                
            print "Shapefile (%s) written." % filename
        

if __name__ == '__main__':
    
    NETWORK_ELIMINATION = False

    mm = MapMatcher()
    
    mm.openShape(BASE_PATH + "SparseNetwork.shp")
    
    print "Road network imported"
    
    print "Parsing road network -> graph"
    mm.shapeToGraph(BASE_PATH + "SparseNetwork.shp", uniqueId="NODE_ID")
    print "Graph generated"
    
    nodes = mm.node_counter__node.values()
    
    for n in nodes:
        dict = {}
        for m in nodes:
            dict[m] = m.getGeometry().distance(n.getGeometry())
        mm.distance_matrix[n] = dict
            
    
    # mm.dumpPointShape("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/points.shp")
    mm.dumpPointShape(BASE_PATH + "spNodes.shp")
    
    for node in nodes:
        edgeStr = ""
        for edge in node.getOutEdges():
            edgeStr = edgeStr + ", " + str(edge.getAttributes().get("ID_NR"))
            # print edge.getAttributes()
        print node.getAttributes() , ": " , edgeStr
    
    #mm.saveGraph("/Users/bsnizek/Projects/Mapmatching/pymapmatching/testdata/Network.yaml")
    #print "Graph saved"
    
    mm.readGPS(BASE_PATH + "GPS_Points.shp")
    
    # max_distance = mm.maxGPSDistance()

    if NETWORK_ELIMINATION:    
        max_distance = 300

        print "The maximum distance between 2 adjacent GPS points is %d" % max_distance
        mm.eliminiateEmptyEdges(distance = max_distance + 0.5)
    
        gts = GraphToShape(mm.G)
        gts.dump(BASE_PATH + "Sparse_bigger0.shp",
                 original_coverage = BASE_PATH + "Network.shp")    
    
    mm.nearPoints()
    print "Near points executed"

    ##selected_label = mm.findRoute(returnNonSelection=False)

    selected_route = mm.findRoutes2()

    print selected_route

    if selected_route:

        if (type(selected_route) == tuple):
            selected_route[0].saveAsShapeFile(BASE_PATH + "SelectedRoute.shp")
            non_selected_counter = 0
            for non_selected in selected_route[1]:
                non_selected.saveAsShapeFile(BASE_PATH + "Nonselected-" + non_selected_counter + ".shp")
                non_selected_counter = non_selected_counter + 1 
        else:
            selected_route.saveAsShapeFile(BASE_PATH + "SelectedRoute.shp")
    else:
        print "No route found"
        
    print "Finished"
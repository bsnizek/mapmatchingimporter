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

from label import Label
from random import shuffle
from networkx.algorithms.shortest_paths.generic import shortest_path

BRIDGE_OVERLAP = 10
MAXIMUM_NUMBER_ROUTES = 100
NODE_OVERLAP = 1
MINIMUM_LENGTH = 0.0

DISTANCE_FACTOR = 1.1


class RouteFinder():
    
    def __init__(self, graph, euclideanOD=None):
        """
        """
        self.graph = graph
        self.bridges = []
        self.results = []
        self.stack = []
        self.EXPAND_COUNTER = 0
        self.euclideanOD = euclideanOD
        self.MAXIMUM_LENGTH = 0.0
        
    

    def findroutes(self, startNode, endNode):
        
        sp = shortest_path(self.graph, startNode, endNode)
        
        i = 1
        sum = 0
        
        while i < len(sp):
            edge_by_nodes = (sp[i-1], sp[i])
            edges = self.graph[edge_by_nodes[0]][edge_by_nodes[1]]
            # import pdb;pdb.set_trace()
            if len(edges.keys()) > 1:
                if edges[0]['edge'].getLength() > edges[1]['edge'].getLength():
                    sum = sum + edges[1]['edge'].getLength()
                else:
                    sum = sum + edges[0]['edge'].getLength()
            else:
                sum = sum + edges[0]['edge'].getLength()
            i = i + 1
        
        self.MAXIMUM_LENGTH = sum * DISTANCE_FACTOR

        startLabel = Label(startNode, parentLabel=None, parentEdge=None, endNode = endNode, routeFinder = self, length=0, star=startNode.getOutEdges())
        self.expand(startLabel, self.MAXIMUM_LENGTH, MINIMUM_LENGTH, endNode)
        
        return self.results
        

    def getMaxLength(self):
        return self.MAXIMUM_LENGTH

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

BRIDGE_OVERLAP = 10
MAXIMUM_NUMBER_ROUTES = 100
MINIMUM_LENGTH = 0.0
MAXIMUM_LENGTH = 2000000000000000000000000000.0
DISTANCE_FACTOR = 5.0
NODE_OVERLAP = 1


class RouteFinder():
    
    def __init__(self, graph):
        """
        """
        self.graph = graph
        self.bridges = []
        self.results = []
        
        
    def expandLabel(self, parentLabel):
        """
        """
        expansion = []   # list of labels
        newLabel = None  #
        
        #out_edges = self.graph.edges(parentLabel.getNode(), self.graph)
        #out_edges = [e[2].get('edge') for e in out_edges]
        
        #print "expanding label at" + str(parentLabel.getNode().getAttributes()) + " " + str(len(out_edges))
        
#        for edge in out_edges:
#            print edge.getAttributes()
            
        print "------"
        print "Length " ,len(parentLabel.getNode().getOutEdges()) , parentLabel.getNode().getAttributes().get("nodecounter") 
        for e in parentLabel.getNode().getOutEdges():
            print "Outedge " , e.getAttributes()
        
        for currentEdge in parentLabel.getNode().getOutEdges():
            # check constraints
            
            # import pdb;pdb.set_trace()
            
            length = parentLabel.getLength() + currentEdge.getLength()
            
            print "currentEdge " + str(currentEdge.getAttributes())

            # newLabel = Label(currentEdge.getToNode(), parent=parentLabel, back_edge=currentEdge, length=length)
            newLabel = Label(currentEdge.getOutNode(parentLabel), parent=parentLabel, back_edge=currentEdge, length=length)
            
#            if len(newLabel.getNode().getOutEdges()) == 1:
#                break
            
#            edgeOccurances = newLabel.getOccurancesOfEdge(newLabel)
            
#            isInBridges = True
#            try:
#                self.bridges.index(newLabel)
#            except ValueError:
#                isInBridges = False
#            
#            if (isInBridges) and edgeOccurances > BRIDGE_OVERLAP:
#                print "break (isInBridges)"
#                break
            
            # path length including this segment longer that MAXIMUM_LENGTH 
            # constraint
            if (length > MAXIMUM_LENGTH):
                print "break (MAXLENGTH)"
                break
            
            print ".."
            
            # euclidean distance to endNode > maxLength * distancefactor
            distanceToEndNode = newLabel.getNode().getGeometry().distance(self.end_node.getGeometry())
            totalLength = newLabel.getLength() + distanceToEndNode
            
            if totalLength > (MAXIMUM_LENGTH * DISTANCE_FACTOR):
                print "break : euclidian distance greater than max"
                break
            
            nodeOccurances = newLabel.getOccurancesOfNode(newLabel.getNode())
            
            if nodeOccurances > NODE_OVERLAP:
                print "node occurance break (%d) at %s." % (nodeOccurances, str(currentEdge.getAttributes()))
                break
            
            self.num_labels = self.num_labels + 1
            expansion.append(newLabel)
            
        return expansion
    
    def checkNodeOverlap(self, label):
        nc = label.getOccurancesOfNode(label.getNode())
        
        return nc > NODE_OVERLAP
    
    def iterative_expansion(self, label):
        print "Checking Label at " , label.getNode().getAttributes()
        if label.getNode() is self.end_node:
            self.results.append(label)
            return None
        else:
            print "Expanding Label at " , label.getNode().getAttributes()
            labels = self.expandLabel2(label)
            for label2 in labels:
                
                print "Checking node overlap for node ", label2.getNode().getAttributes().get("nodecounter")
                
                if not self.checkNodeOverlap(label2):
                    self.iterative_expansion(label2)
                else:
                    print "--"
            
            
          
    def expandLabel2(self, parentLabel):
        """
        Expands a label and returns the labels of the expanded edges
        """
        
        out_edges = parentLabel.getNode().getOutEdges()
        for oe in out_edges:
            print "outEdge " , oe.getAttributes().get("ID_NR")
            
        labels =  [Label(edge.getOutNode(parentLabel), 
                         parent=parentLabel, 
                         back_edge=edge) for edge in out_edges]
        return labels
        
            
    def findroutes(self, start_node, end_node):
        self.start_node = start_node
        self.end_node = end_node
        
        self.startLabel = Label(self.start_node, parentLabel=None, parentEdge=None, endNode=self.end_node, routeFinder=self)
        self.startLabel.expand(MAXIMUM_LENGTH, MINIMUM_LENGTH, endNode=self.end_node)
        
        # print "startnode " + str(self.start_node.getAttributes()) + " " + str(self.start_node.getPoint())
        # print "endnode " + str(self.end_node.getAttributes())
        
        #currentlabel = Label(self.start_node)
        
        #self.iterative_expansion(currentlabel)
               
        return self.results
                
    def isValidRoute(self, label):
        #if not label.getNode() != self.end_node and label.getLength() >= MINIMUM_LENGTH and label.getLength() <= MAXIMUM_LENGTH:
        #    import pdb;pdb.set_trace()
        return label.getNode() == self.end_node and label.getLength() >= MINIMUM_LENGTH and label.getLength() <= MAXIMUM_LENGTH
    
    

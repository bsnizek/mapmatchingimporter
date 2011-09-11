'''
Created on May 31, 2011

@author: bsnizek
'''
import networkx as nx

from networkx.algorithms.cycles import *

class Node:
    
    def __init__(self, id):
        self.id = id
        
    def getID(self):
        return self.id
        
class Edge:
    
    def __init__(self, id, node1, node2):
        self.id = id
        self.node1 = node1
        self.node2 = node2


if __name__ == '__main__':
    
    # G = nx.Graph()
    
    G = nx.MultiGraph()
    
    n0 = Node(id=0)
    n1 = Node(id=1)
    n2 = Node(id=2)
    n3 = Node(id=3)
    n4 = Node(id=4)
    n5 = Node(id=5)
    n6 = Node(id=6)
    n7 = Node(id=7)
    
    e1 = Edge('A', n0, n2)
    e2 = Edge('B', n2, n0)
    e3 = Edge('C', n2, n4)
    e4 = Edge('D', n4, n5)
    e5 = Edge('E', n3, n4)
    e6 = Edge('F', n3, n7)
    e7 = Edge('G', n6, n3)
    e8 = Edge('H', n0, n1)
    e9 = Edge('I', n0, n3)
    
    G.add_edge(n0, n2, data={'edge' : e1})
    #G.add_edge(n2, n0, data={'edge' : e1})
    
    G.add_edge(n0, n2, data={'egge' : e2})
    #G.add_edge(n2, n0, data={'egge' : e2})
    
    G.add_edge(n2, n4, data={'edge' : e3})
    #G.add_edge(n4, n2, data={'edge' : e3})
    
    G.add_edge(n4, n5, data={'edge' : e4})
    #G.add_edge(n5, n4, data={'edge' : e4})
     
    G.add_edge(n3, n4, data={'edge' : e5})
    #G.add_edge(n4, n3, data={'edge' : e5})

    
    G.add_edge(n3, n7, data={'egge' : e6})
    #G.add_edge(n7, n3, data={'egge' : e6})
    
    G.add_edge(n6, n3, data={'edge' : e7})
    #G.add_edge(n3, n6, data={'edge' : e7})
    
    G.add_edge(n0, n1, data={'edge' : e8})
    #G.add_edge(n1, n0, data={'edge' : e8})
    
    G.add_edge(n0, n3, data={'edge' : e9})
    #G.add_edge(n3, n0, data={'edge' : e9})
    
    from networkx.algorithms.traversal.depth_first_search import *
    from networkx.algorithms.traversal.breadth_first_search import *
    
    fw = dfs_labeled_edges(G, n7)
    for (f1,f2, dir) in fw:
        print f1.getID()," ", f2.getID(), " ", dir

    def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not graph.has_key(start):
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths   
    
    graph = {'A': ['B', 'C'],
             'B': ['C', 'D'],
             'C': ['D'],
             'D': ['C'],
             'E': ['F'],
             'F': ['C']}
    
    print find_all_paths(graph, 'A', 'D')



            
    
    
        
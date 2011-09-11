'''
Created on May 31, 2011

@author: bsnizek
'''
from rtree import Rtree

if __name__ == '__main__':
    
    idx = Rtree()
    minx, miny, maxx, maxy = (0.0, 0.0, 0.0, 0.0)
    idx.add(0, (minx, miny, maxx, maxy))
    print list(idx.intersection((-1.0, -1.0, 1.0, 1.0)))
    
    
    
        
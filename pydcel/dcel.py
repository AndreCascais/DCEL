from __future__ import print_function
import numpy as np
from bintrees import AVLTree

from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])

class vertex(object):
    
    def __init__(self, px, py, identifier):
        self.identifier = identifier
        self.x = px
        self.y = py
        self.incidentEdge = None
        self.isReflex = False
        
    def setTopology(self, newIncedentEdge):
        self.incidentEdge = newIncedentEdge
        
    def p(self):
        return (self.x,self.y)

    def __repr__(self):
        return "v{} ({}, {})".format(self.identifier, self.x, self.y)
    
    def checkReflex(self):
        prev = self.incidentEdge.previous.origin
        post = self.incidentEdge.next.origin

        v1 = np.array([self.x - prev.x, self.y - prev.y])
        v2 = np.array([post.x - self.x, post.y - self.y])

        # reflex, same line, same line
        if (np.cross(v1, v2) == -1 or v1[0] == v2[0]) :
            self.isReflex = True
        else:
            self.isReflex = False

class hedge(object):
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.origin = None
        self.twin = None
        self.incidentFace = None
        self.next = None
        self.previous = None

    def setTopology(self, newOrigin, newTwin, newIncindentFace, newNext, newPrevious):
        self.origin = newOrigin
        self.twin = newTwin
        self.incidentFace = newIncindentFace
        self.next = newNext
        self.previous = newPrevious
        
    def loop(self):
        """Loop from this hedge to the next ones. Stops when we are at the current one again."""
        yield self
        e = self.next
        while e is not self:
            yield e
            e = e.next
            
    def wind(self):
        """iterate over hedges emerging from vertex at origin in ccw order"""
        yield self
        e = self.previous.twin
        while e is not self:
            yield e
            e = e.previous.twin

    def __repr__(self):
        return "he{}".format(self.identifier)

    def getDirection(self):
        if (self.origin.x > self.next.origin.x):
            return 'l'
        elif (self.origin.x < self.next.origin.x):
            return 'r'
        elif (self.origin.y > self.next.origin.y):
            return 'd'
        elif (self.origin.y < self.next.origin.y):
            return 'u'



class face(object):
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.outerComponent = None
        self.innerComponent = None

    def setTopology(self, newOuterComponent, newInnerComponent=None):
        self.outerComponent = newOuterComponent
        self.innerComponent = newInnerComponent
        
    def loopOuterVertices(self):
        for e in self.outerComponent.loop():
            yield e.origin

    def __repr__(self):
        # return "face( innerComponent-{}, outerComponent-{} )".format(self.outerComponent, self.innerComponent)
        return "f{}".format(self.identifier)


def findIntersection(horizontal,vertical):
    x = vertical.origin.x
    y = horizontal.origin.y
    return Point(x,y)


class DCEL(object):
    
    def __init__(self):
        self.vertexList = []
        self.hedgeList = []
        self.faceList = []
        self.infiniteFace = None
        self.eventList = []

    def getNewId(self, L):
        if len(L) == 0:
            return 0
        else:
            return L[-1].identifier + 1
        
    def createVertex(self, px, py):
        identifier = self.getNewId(self.vertexList)
        v = vertex(px,py, identifier)
        self.vertexList.append(v)
        return v
        
    def createHedge(self):
        identifier = self.getNewId(self.hedgeList)
        e = hedge(identifier)
        self.hedgeList.append(e)
        return e
        
    def createFace(self):
        identifier = self.getNewId(self.faceList)
        f = face(identifier)
        self.faceList.append(f)
        return f

    def createInfFace(self):
        identifier = "i"
        f = face(identifier)
        self.infiniteFace = f
        return f
        
    def remove(self, element):
        # TODO: verify topology? i.e. make sure no reference to element exists...
        if type(element) is vertex:
            self.vertexList.remove(element)
            del element
        elif type(element) is hedge:
            self.hedgeList.remove(element)
            del element
        elif type(element) is face:
            self.faceList.remove(element)
            del element
        else:
            print("illegal element type")

    def __repr__(self):
        s = ""
        for v in self.vertexList:
            s += "{} : \t{}\n".format(v, v.incidentEdge)
        for e in self.hedgeList:
            s += "{} : \t{} \t{} \t{} \t{} \t{}\n".format(e, e.origin, e.twin, e.incidentFace, e.next, e.previous)
        for f in self.faceList + [self.infiniteFace]:
            s += "{} : \t{} \t{}\n".format(f, f.outerComponent, f.innerComponent)
        return s

    def checkEdgeTwins(self):
        for e in self.hedgeList:
            if not e == e.twin.twin:
                print("this edge has a problem with its twin:",e)
            
    def separateHedges(self):
        """
        separates vertical and horizontal edges
        the ones chosen didnt had the incident face being inf
        """
        for i in self.hedgeList:
            if (i.incidentFace.identifier  != "i"):
                self.eventList.append(i)
        self.eventList = sorted(self.eventList, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
        
        
    def horizontalSweep(self):
        for vertex in self.vertexList:
            vertex.checkReflex()
        sweepingLine = AVLTree()
        
        for hedge in self.eventList:
            myDir = hedge.getDirection()
            prevDir = hedge.previous.getDirection()
            
            # expand
            if hedge.origin.isReflex:
                possibleDirs = ['l', 'r']
                if myDir == 'l' or prevDir == 'r':
                    possibleDirs.remove('l')
                if myDir == 'r' or prevDir == 'l':
                    possibleDirs.remove('r')
                    
                # esquerda -> edge tem de descer
                # direita -> edge tem de subir
                
                if 'l' in possibleDirs:
                    leftHedge = sweepingLine.floor_item(hedge.origin.x - 1)[1]
                    if (leftHedge.getDirection() == 'd'):

                        coords = findIntersection(hedge,leftHedge)
                        old_vert = hedge.origin
                        new_vert = self.createVertex(coords.x, coords.y)
                        
                        # Break incident edge in two
                        new_v_hedge = self.createHedge()
                        new_v_twin_hedge = self.createHedge()

                        new_vert.incidentEdge = leftHedge

                        new_v_hedge.setTopology(leftHedge.origin, new_v_twin_hedge, leftHedge.incidentFace, leftHedge, leftHedge.previous)
                        new_v_hedge.origin.incidentEdge = new_v_hedge
                        new_v_twin_hedge.setTopology(new_vert, new_v_hedge, leftHedge.twin.incidentFace, leftHedge.twin.next, leftHedge.twin.previous)
    
                        leftHedge.origin = new_vert

                        leftHedge.previous.next = new_v_hedge
                        leftHedge.previous = new_v_hedge

                        leftHedge.twin.next.previous = new_v_twin_hedge
                        leftHedge.twin.next = new_v_twin_hedge
                    
                        # Join new hedge
                        
                        new_hedge = self.createHedge()
                        twin_for_new_hedge = self.createHedge()

                        new_hedge.setTopology(new_vert, twin_for_new_hedge, hedge.incidentFace, hedge, new_v_hedge)
                        twin_for_new_hedge.setTopology(old_vert, new_hedge, hedge.incidentFace, leftHedge, hedge.twin.next.twin)

                        # Isto esta mal
                        hedge.next.previous = new_hedge
                        hedge.next = new_hedge.twin
                        

                if 'r' in possibleDirs:
                    rightHedge = sweepingLine.ceiling_item(hedge.origin.x + 1)[1]
                    if (rightHedge.getDirection() == 'u'):

                        coords = findIntersection(hedge, rightHedge)
                        old_vert = hedge.origin
                        new_vert = self.createVertex(coords.x, coords.y)
                        
                        # Break incident edge in two
                        new_v_hedge = self.createHedge()
                        new_v_twin_hedge = self.createHedge()

                        new_vert.incidentEdge = new_v_hedge
                        
                        new_v_hedge.setTopology(new_vert, new_v_twin_hedge, rightHedge.incidentFace, rightHedge.next, rightHedge)

                        new_v_twin_hedge.setTopology(rightHedge.twin.origin, new_v_hedge, rightHedge.twin.incidentFace, rightHedge.twin, rightHedge.twin.previous)
    
                        rightHedge.twin.origin = new_vert

                        rightHedge.next.previous = new_v_hedge
                        rightHedge.next = new_v_hedge

                        rightHedge.twin.previous.next = new_v_twin_hedge
                        rightHedge.twin.previous = new_v_twin_hedge
                    
                        # Join new hedge
                        
                        new_hedge = self.createHedge()
                        twin_for_new_hedge = self.createHedge()

                        new_hedge.setTopology(old_vert, twin_for_new_hedge, hedge.incidentFace, new_v_hedge, hedge.twin.next.twin)
                        twin_for_new_hedge.setTopology(new_vert, new_hedge, hedge.incidentFace, hedge, rightHedge)
                        new_v_hedge.origin.incidentEdge = new_v_hedge
                        
                        hedge.previous.next = new_hedge
                        hedge.previous = new_hedge.twin

                    

            # start
            if myDir == 'd':
                # direction da sweeping line -> add vertex 
                sweepingLine.insert(hedge.origin.x, hedge)
            elif prevDir == 'u':
                sweepingLine.insert(hedge.previous.origin.x, hedge.previous)
                
            # close
            if myDir == 'u':
                sweepingLine.remove(hedge.origin.x)
            elif prevDir == 'd':
                sweepingLine.remove(hedge.previous.origin.x)
                    
                    


# class compHedge:
#     def __init__(self, hedge, key):
#         self.hedge = hedge
#         self.key = key
#     def __lt_(self, hedge2):
#         print("lt", self, hedge2, " < ", self.key < hedge2.key)
#         return self.key < hedge2.key
#     def __eq__(self, hedge2):
#         print("eq", self, hedge2, " = ", self.key == hedge2.key)
#         return self.key == hedge2.key
#     def __repr__(self):
#         return self.hedge.__repr__()
#
#
# def orderSweep(l):
#     l = sorted(l, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
#     return l

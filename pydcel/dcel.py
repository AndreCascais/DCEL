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

    def __repr__(self):
        s = ""
        for v in self.vertexList:
            s += "{} : \t{}\n".format(v, v.incidentEdge)
        for e in self.hedgeList:
            s += "{} : \t{} \t{} \t{} \t{} \t{}\n".format(e, e.origin, e.twin, e.incidentFace, e.next, e.previous)
        for f in self.faceList + [self.infiniteFace]:
            s += "{} : \t{} \t{}\n".format(f, f.outerComponent, f.innerComponent)
        return s

            
    def separateHedges(self):
        """
        separates vertical and horizontal edges
        the ones chosen didnt had the incident face being inf
        """
        events = []
        for i in self.hedgeList:
            if (i.incidentFace.identifier  != "i"):
                events.append(i)
        events = sorted(events, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
        l = []
        for i in events:
            if l == [] or l[0].origin.y == i.origin.y:
                l.append(i)
            else:
                self.eventList.append(l)
                l = []
                l.append(i)
        
        
    def horizontalSweep(self):
        for vertex in self.vertexList:
            vertex.checkReflex()
        sweeping_line = AVLTree()
        
        for l in self.eventList:
            # one cycle to add hedges
            for hedge in l:
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()
                # start
                if my_dir == 'd':
                    # direction da sweeping line -> add vertex 
                    sweeping_line.insert(hedge.origin.x, hedge)
                elif prev_dir == 'u':
                    sweeping_line.insert(hedge.previous.origin.x, hedge.previous)
                    
            # another to close/expand
            for hedge in l:
                print("Sweeping line now is :", sweeping_line, "on ", hedge.origin.y)
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()
                # close
                if my_dir == 'u':
                    sweeping_line.remove(hedge.origin.x)
                elif prev_dir == 'd':
                    sweeping_line.remove(hedge.previous.origin.x)
                # expand
                #            if hedge.origin.isReflex:

                if not sweeping_line.is_empty():
                    possible_dirs = ['l', 'r']
                    if my_dir == 'l' or prev_dir == 'r':
                        possible_dirs.remove('l')
                    if my_dir == 'r' or prev_dir == 'l':
                        possible_dirs.remove('r')

                    # esquerda -> edge tem de descer
                    # direita -> edge tem de subir

                    if 'l' in possible_dirs and hedge.origin.x > sweeping_line.min_item()[0]:
                        left_hedge = sweeping_line.floor_item(hedge.origin.x - 1)[1]
                        if (left_hedge.getDirection() == 'd'):

                            coords = findIntersection(hedge,left_hedge)
                            old_vert = hedge.origin
                            new_vert = self.createVertex(coords.x, coords.y)

                            # Break incident edge in two
                            new_v_hedge = self.createHedge()
                            new_v_twin_hedge = self.createHedge()

                            new_vert.incidentEdge = left_hedge

                            new_v_hedge.setTopology(left_hedge.origin, new_v_twin_hedge, left_hedge.incidentFace, left_hedge, left_hedge.previous)
                            new_v_hedge.origin.incidentEdge = new_v_hedge
                            new_v_twin_hedge.setTopology(new_vert, new_v_hedge, left_hedge.twin.incidentFace, left_hedge.twin.next, left_hedge.twin)

                            left_hedge.origin = new_vert

                            left_hedge.previous.next = new_v_hedge
                            left_hedge.previous = new_v_hedge

                            left_hedge.twin.next.previous = new_v_twin_hedge
                            left_hedge.twin.next = new_v_twin_hedge

                            # Join new hedge
                            # new_h_hedge -> above hedge
                            new_h_hedge = self.createHedge()
                            new_h_twin_hedge = self.createHedge()

                            new_h_hedge.setTopology(new_vert, new_h_twin_hedge, hedge.incidentFace, hedge, new_v_hedge)
                            new_h_twin_hedge.setTopology(old_vert, new_h_hedge, hedge.incidentFace, left_hedge, hedge.previous)

                            # Atualizacoes

                            hedge.previous.next = new_h_twin_hedge
                            hedge.previous = new_h_hedge

                            new_v_hedge.next.previous = new_h_twin_hedge
                            new_v_hedge.next = new_h_hedge


                    if 'r' in possible_dirs and hedge.origin.x < sweeping_line.max_item()[0]:

                        right_hedge = sweeping_line.ceiling_item(hedge.origin.x + 1)[1]

                        if (right_hedge.getDirection() == 'u'):

                            coords = findIntersection(hedge, right_hedge)
                            old_vert = hedge.origin
                            new_vert = self.createVertex(coords.x, coords.y)

                            # Break incident edge in two
                            new_v_hedge = self.createHedge()
                            new_v_twin_hedge = self.createHedge()

                            new_vert.incidentEdge = new_v_hedge

                            new_v_hedge.setTopology(new_vert, new_v_twin_hedge, right_hedge.incidentFace, right_hedge.next, right_hedge)

                            new_v_twin_hedge.setTopology(right_hedge.twin.origin, new_v_hedge, right_hedge.twin.incidentFace, right_hedge.twin, right_hedge.twin.previous)

                            right_hedge.twin.origin = new_vert

                            right_hedge.next.previous = new_v_hedge
                            right_hedge.next = new_v_hedge

                            right_hedge.twin.previous.next = new_v_twin_hedge
                            right_hedge.twin.previous = new_v_twin_hedge

                            # Join new hedge

                            #new_h_hedge fica abaixo
                            new_h_hedge = self.createHedge()
                            new_h_twin_hedge = self.createHedge()

                            new_h_hedge.setTopology(old_vert, new_h_twin_hedge, hedge.incidentFace, new_v_hedge, hedge.previous)
                            new_h_twin_hedge.setTopology(new_vert, new_h_hedge, hedge.incidentFace, hedge, right_hedge)

                            #Atualizacoes

                            hedge.previous.next = new_h_hedge
                            hedge.previous = new_h_twin_hedge

                            new_v_hedge.previous.next = new_h_twin_hedge
                            new_v_hedge.previous = new_h_hedge


                          
#
# def orderSweep(l):
#     l = sorted(l, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
#     return l

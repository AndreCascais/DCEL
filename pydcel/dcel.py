from __future__ import print_function
import numpy as np
from bintrees import AVLTree

from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])

XMinus, XPlus, YMinus, YPlus = range(4)

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
        
    def findIntersection(self, vertex):
        # Check whether self is horizontal or vertical
        if (self.origin.y == self.next.origin.y): #self is horizontal
            x = vertex.x
            y = self.origin.y
        else: # self is vertical
            x = self.origin.x
            y = vertex.y
        return Point(x,y)



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

            
    def separateHedges(self, direction):
        """
        separates vertical and horizontal edges
        the ones chosen didnt had the incident face being inf
        """
        self.eventList = []
        events = []
        for i in self.hedgeList:
            if (i.incidentFace.identifier  != "i"):
                events.append(i)
        if (direction == 'h'):
            events = sorted(events, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
        else:
            events = sorted(events, key = lambda x: (x.origin.x, x.origin.y), reverse = True)
        l = []
        for i in events:
            if l == [] or (l[0].origin.y == i.origin.y and direction == 'h') or (l[0].origin.x == i.origin.x and direction == 'v'):
                l.append(i)
            else:
                self.eventList.append(l)
                l = []
                l.append(i)
        self.eventList.append(l)
        
    def divideHedge (self, hedge, point, direction):
        
        new_vert = self.createVertex(point.x, point.y)
        
        # Break incident edge in two
        new_hedge = self.createHedge()
        new_twin_hedge = self.createHedge()

        if (direction == 'd' or direction == 'l'):
            #new_vert.incidentEdge = hedge

            new_hedge.setTopology(hedge.origin, new_twin_hedge, hedge.incidentFace, hedge, hedge.previous)
            #new_hedge.origin.incidentEdge = new_hedge
            new_twin_hedge.setTopology(new_vert, new_hedge, hedge.twin.incidentFace, hedge.twin.next, hedge.twin)
            
            hedge.origin = new_vert
            
            hedge.previous.next = new_hedge
            hedge.previous = new_hedge
            
            hedge.twin.next.previous = new_twin_hedge
            hedge.twin.next = new_twin_hedge

        elif (direction == 'u' or direction == 'r'):
        
            new_hedge.setTopology(new_vert, new_twin_hedge, hedge.incidentFace, hedge.next, hedge)
            new_twin_hedge.setTopology(hedge.twin.origin, new_hedge, hedge.twin.incidentFace, hedge.twin, hedge.twin.previous)
        
            hedge.twin.origin = new_vert
            
            hedge.next.previous = new_hedge
            hedge.next = new_hedge
            
            hedge.twin.previous.next = new_twin_hedge
            hedge.twin.previous = new_twin_hedge
            

    def joinHedges(self, hedge, new_hedge, old_vert, new_vert, direction):
        # Join new hedge

        new_j_hedge = self.createHedge()
        new_j_twin_hedge = self.createHedge()

        if (direction == 'l' or direction == 'u'):
            # new_j_hedge -> above hedge
            new_j_hedge.setTopology(new_vert, new_j_twin_hedge, hedge.incidentFace, hedge, new_hedge)
            new_j_twin_hedge.setTopology(old_vert, new_j_hedge, hedge.incidentFace, new_hedge.next, hedge.previous)
        
            # Updates
        
            hedge.previous.next = new_j_twin_hedge
            hedge.previous = new_j_hedge
        
            new_hedge.next.previous = new_j_twin_hedge
            new_hedge.next = new_j_hedge
        elif (direction == 'r'):
            #new_h_hedge fica abaixo
            new_j_hedge.setTopology(old_vert, new_j_twin_hedge, hedge.incidentFace, new_hedge, hedge.previous)
            new_j_twin_hedge.setTopology(new_vert, new_j_hedge, hedge.incidentFace, hedge, new_hedge.next)
            
            #Atualizacoes
            
            hedge.previous.next = new_j_hedge
            hedge.previous = new_j_twin_hedge
            
            new_hedge.previous.next = new_j_twin_hedge
            new_hedge.previous = new_j_hedge
        elif (direction == 'd'):
            #new_j_edge -> right
            new_j_hedge.setTopology(old_vert, new_j_twin_hedge, hedge.incidentFace, new_hedge, hedge.previous)
            new_j_twin_hedge.setTopology(new_vert, new_j_hedge, hedge.incidentFace, hedge, new_hedge.previous)

            #updates

            hedge.previous.next = new_j_hedge
            hedge.previous = new_j_twin_hedge

            new_hedge.previous.next = new_j_twin_hedge
            new_hedge.previous = new_j_hedge
            
            
    def horizontalSweep(self):

        sweeping_line = AVLTree()
        
        for l in self.eventList:
            # one cycle to add hedges
            for hedge in l:
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()
                # start
                if my_dir == 'd':
                    # direction of sweeping line -> add vertex
                    sweeping_line.insert(hedge.origin.x, hedge)
                elif prev_dir == 'u':
                    sweeping_line.insert(hedge.previous.origin.x, hedge.previous)
                    
            # another to close/expand them
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

                if not sweeping_line.is_empty(): # only try to expand if sweeping line is not empty
                    possible_dirs = ['l', 'r']
                    if my_dir == 'l' or prev_dir == 'r':
                        possible_dirs.remove('l')
                    if my_dir == 'r' or prev_dir == 'l':
                        possible_dirs.remove('r')

                    # going left -> hedge must go down
                    # going right -> hedge must go up

                    if 'l' in possible_dirs and hedge.origin.x > sweeping_line.min_item()[0]:
                        left_hedge = sweeping_line.floor_item(hedge.origin.x - 1)[1]
                        if (left_hedge.getDirection() == 'd'):
                            old_vert = hedge.origin
                            if (left_hedge.origin.y == hedge.origin.y):
                                new_v_hedge = left_hedge.previous
                                new_vert = left_hedge.origin
                            elif (left_hedge.next.origin.y == hedge.origin.y):
                                new_v_hedge = left_hedge
                                new_vert = left_hedge.next.origin
                            else:
                                coords = left_hedge.findIntersection(old_vert)
                                new_vert = self.createVertex(coords.x, coords.y)
                                self.divideHedge(left_hedge, coords, 'd')
                                new_v_hedge = left_hedge.previous
                                
                            self.joinHedges(hedge, new_v_hedge, old_vert, new_vert, 'l')


                    if 'r' in possible_dirs and hedge.origin.x < sweeping_line.max_item()[0]:
                        right_hedge = sweeping_line.ceiling_item(hedge.origin.x + 1)[1]

                        if (right_hedge.getDirection() == 'u'):
                            old_vert = hedge.origin
                            coords = right_hedge.findIntersection(old_vert)
                            new_vert = self.createVertex(coords.x, coords.y)
                            self.divideHedge(right_hedge, coords, 'u')
                            new_v_hedge = right_hedge.next
                            self.joinHedges(hedge, new_v_hedge, old_vert, new_vert, 'r')
                            

                          
    def verticalSweep(self):

        sweeping_line = AVLTree()
        
        for l in self.eventList:
            # one cycle to add hedges
            print (l)
            for hedge in l:
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()
                # start
                if my_dir == 'l':
                    # direction of sweeping line -> add vertex
                    sweeping_line.insert(hedge.origin.y, hedge)
                elif prev_dir == 'r':
                    sweeping_line.insert(hedge.previous.origin.y, hedge.previous)
                    
            # another to close/expand them
            for hedge in l:
                print("Sweeping line now is :", sweeping_line, "on ", hedge.origin.x)
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()
                # close
                if my_dir == 'r':
                    sweeping_line.remove(hedge.origin.y)
                elif prev_dir == 'l':
                    sweeping_line.remove(hedge.previous.origin.y)
                    
                #print("Sweeping before expanding now is :", sweeping_line, "on ", hedge.origin.x)
            # expand

                if not sweeping_line.is_empty(): # only try to expand if sweeping line is not empty
                    possible_dirs = ['u', 'd']
                    if my_dir == 'u' or prev_dir == 'd':
                        possible_dirs.remove('u')
                    if my_dir == 'd' or prev_dir == 'u':
                        possible_dirs.remove('d')

                    # going up -> hedge must go left
                    # going down -> hedge must go right
                    print (hedge, "Can go to", possible_dirs)

                    if 'd' in possible_dirs and hedge.origin.y > sweeping_line.min_item()[0]:
                        down_hedge = sweeping_line.floor_item(hedge.origin.y - 1)[1]
                        if (down_hedge.getDirection() == 'r'):
                            old_vert = hedge.origin
                            if (down_hedge.origin.x == hedge.origin.x): # So vou tratar else
                                new_v_hedge = left_edge.previous
                                new_vert = left_hedge.origin
                            elif (down_hedge.next.origin.x == hedge.origin.x):
                                new_v_hedge = left_hedge
                                new_vert = left_hedge.next.origin
                            else:
                                coords = down_hedge.findIntersection(old_vert)
                                new_vert = self.createVertex(coords.x, coords.y)
                                self.divideHedge(down_hedge, coords, 'r')
                                new_h_hedge = down_hedge.next
                                
                            self.joinHedges(hedge, new_h_hedge, old_vert, new_vert, 'd')


                    if 'u' in possible_dirs and hedge.origin.y < sweeping_line.max_item()[0]:
                        up_hedge = sweeping_line.ceiling_item(hedge.origin.y + 1)[1]

                        if (up_hedge.getDirection() == 'l'):
                            old_vert = hedge.origin
                            coords = up_hedge.findIntersection(old_vert)
                            new_vert = self.createVertex(coords.x, coords.y)
                            self.divideHedge(up_hedge, coords, 'l')
                            new_h_hedge = up_hedge.previous
                            self.joinHedges(hedge, new_h_hedge, old_vert, new_vert, 'u')
    

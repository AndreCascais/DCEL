from __future__ import print_function
import numpy as np
from bintrees import AVLTree
import copy
from segments import *
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
        return self.x, self.y
    
    def toPoint(self):
        return Point(self.x, self.y)

    def __repr__(self):
        return "v{} ({}, {})".format(self.identifier, self.x, self.y)
    
    def checkReflex(self):
        prev = self.incidentEdge.previous.origin
        post = self.incidentEdge.next.origin

        v1 = np.array([self.x - prev.x, self.y - prev.y])
        v2 = np.array([post.x - self.x, post.y - self.y])

        # reflex, same line, same line
        if np.cross(v1, v2) == -1 or v1[0] == v2[0]:
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
        if self.origin.x > self.next.origin.x:
            return 'l'
        elif self.origin.x < self.next.origin.x:
            return 'r'
        elif self.origin.y > self.next.origin.y:
            return 'd'
        elif self.origin.y < self.next.origin.y:
            return 'u'
        
    def findIntersection(self, vertex):
        # Check whether self is horizontal or vertical
        if self.origin.y == self.next.origin.y:  # self is horizontal
            x = vertex.x
            y = self.origin.y
        else:  # self is vertical
            x = self.origin.x
            y = vertex.y
        return Point(x, y)
    
    def isTwinBlocking(self, direction):
        if direction == 'u':  # if i go left my twin goes right and is above me -> blocks
            return self.getDirection() == 'l'
        elif direction == 'd':
            return self.getDirection() == 'r'

    def toSegment(self):
        src = self.origin.toPoint()
        dest = self.next.origin.toPoint()
        return Segment(src, dest)


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
        self.vertexSet = set()
        self.segmentList = SegmentList()
        self.vertexVisibility = None
        self.faceVisibility = None
        
    def computeVertexVisibility(self):
        dim = len(self.vertexList)
        self.vertexVisibility = np.zeros((dim, dim))
        for i in range(dim):
            for j in range(i + 1):
                segment = Segment(self.vertexList[i].toPoint(), self.vertexList[j].toPoint())
                if (not self.segmentList.canIntersect(segment)):
                    self.vertexVisibility[i, j] = 1
        print (self.vertexVisibility)
        
    def hedgesToSegments(self):
        for i in self.eventList:
            for j in i:
                segment = j.toSegment()
                self.segmentList.addSegment(segment)
    
    def getNewId(self, a_list):
        if len(a_list) == 0:
            return 0
        else:
            return a_list[-1].identifier + 1

    def createVertex(self, px, py):
        identifier = self.getNewId(self.vertexList)
        v = vertex(px, py, identifier)
        self.vertexList.append(v)
        self.vertexSet.add(Point(px,py))
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

    def renameFaces(self):
        copy_of_edge_list = copy.copy(self.hedgeList)
        flag_first = True
        while len(copy_of_edge_list) != 0:

            some_initial_edge = copy_of_edge_list.pop(0)

            if some_initial_edge.incidentFace != self.infiniteFace:

                if not flag_first:
                    new_face = self.createFace()
                    new_face.setTopology(some_initial_edge)
                else:
                    new_face = some_initial_edge.incidentFace
                    flag_first = False

                some_initial_edge.incidentFace = new_face
                current_edge = some_initial_edge.next

                while True:
                    if some_initial_edge == current_edge:
                        break
                    else:
                        print("adding hedge {} to face {}".format(current_edge, new_face))
                        current_edge.incidentFace = new_face
                        copy_of_edge_list.remove(current_edge)
                        current_edge = current_edge.next

    def separateHedges(self, direction):
        """
        separates vertical and horizontal edges
        ignore the ones whose incident face is the infinite face
        """
        self.eventList = []
        events = []
        for i in self.hedgeList:
            if i.incidentFace.identifier != "i":
                events.append(i)

        if direction == 'h':
            events = sorted(events, key=lambda h: (h.origin.y, h.origin.x), reverse=True)
        else:
            events = sorted(events, key=lambda h: (h.origin.x, -h.origin.y), reverse=True)

        l = []
        for i in events:
            if l == [] or (l[0].origin.y == i.origin.y and direction == 'h') or (l[0].origin.x == i.origin.x and direction == 'v'):
                l.append(i)
            else:
                self.eventList.append(l)
                l = [i]
        self.eventList.append(l)

    def divideHedge(self, a_hedge, point, direction):

        new_vert = self.createVertex(point.x, point.y)
        print("I've just create a new vert", new_vert)

        # Break incident edge in two
        new_hedge = self.createHedge()
        new_twin_hedge = self.createHedge()

        if direction == 'd' or direction == 'l':

            new_hedge.setTopology(a_hedge.origin, new_twin_hedge, a_hedge.incidentFace, a_hedge, a_hedge.previous)
            new_twin_hedge.setTopology(new_vert, new_hedge, a_hedge.twin.incidentFace, a_hedge.twin.next, a_hedge.twin)

            a_hedge.origin = new_vert

            a_hedge.previous.next = new_hedge
            a_hedge.previous = new_hedge

            a_hedge.twin.next.previous = new_twin_hedge
            a_hedge.twin.next = new_twin_hedge

        elif direction == 'u' or direction == 'r':

            new_hedge.setTopology(new_vert, new_twin_hedge, a_hedge.incidentFace, a_hedge.next, a_hedge)
            new_twin_hedge.setTopology(a_hedge.twin.origin, new_hedge, a_hedge.twin.incidentFace, a_hedge.twin, a_hedge.twin.previous)

            a_hedge.twin.origin = new_vert

            a_hedge.next.previous = new_hedge
            a_hedge.next = new_hedge

            a_hedge.twin.previous.next = new_twin_hedge
            a_hedge.twin.previous = new_twin_hedge

        new_hedge.origin.incidentEdge = new_hedge
        new_vert.incidentEdge = hedge

        return new_vert

    def joinHedges(self, a_hedge, new_hedge, old_vert, new_vert, direction):
        new_j_hedge = self.createHedge()
        new_j_twin_hedge = self.createHedge()

        if direction == 'l' or direction == 'u':
            # Setup new hedge and its twin

            new_j_hedge.setTopology(new_vert, new_j_twin_hedge, a_hedge.incidentFace, a_hedge, new_hedge)
            new_j_twin_hedge.setTopology(old_vert, new_j_hedge, a_hedge.incidentFace, new_hedge.next, a_hedge.previous)

            # Update pointers between edges

            a_hedge.previous.next = new_j_twin_hedge
            a_hedge.previous = new_j_hedge

            new_hedge.next.previous = new_j_twin_hedge
            new_hedge.next = new_j_hedge

        elif direction == 'r' or direction == 'd':
            # Setup new hedge and its twin
            new_j_hedge.setTopology(old_vert, new_j_twin_hedge, a_hedge.incidentFace, new_hedge, a_hedge.previous)
            new_j_twin_hedge.setTopology(new_vert, new_j_hedge, a_hedge.incidentFace, a_hedge, new_hedge.previous)

            # Update pointers between edges

            a_hedge.previous.next = new_j_hedge
            a_hedge.previous = new_j_twin_hedge

            new_hedge.previous.next = new_j_twin_hedge
            new_hedge.previous = new_j_hedge

    def horizontalSweep(self):

        sweeping_line = AVLTree()

        for l in self.eventList:

            print("List on", l[0].origin.y, "contains events: ", l)

            # one cycle to add hedges to the sweeping line
            for hedge in l:

                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()

                if my_dir == 'd':
                    # direction of sweeping line -> add vertex
                    sweeping_line.insert(hedge.origin.x, hedge)
                elif prev_dir == 'u':
                    sweeping_line.insert(hedge.previous.origin.x, hedge.previous)

            to_be_removed = set()

            # another cycle to find hedges to be closed
            for hedge in l:

                print("Sweeping Line :", sweeping_line, "on x:", hedge.origin.x, "on y:,", hedge.origin.y, "and event", hedge)
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()

                # add hedges that will be closed later
                if my_dir == 'u':
                    print("hedge {} wants to remove {}".format(hedge, hedge))
                    to_be_removed.add(hedge.origin.x)
                elif prev_dir == 'd':
                    print("hedge {} wants to remove {}".format(hedge, hedge.previous))
                    to_be_removed.add(hedge.previous.origin.x)

            # another cycle to expand hedges
            for hedge in l:
                if not sweeping_line.is_empty():  # only try to expand if sweeping line is not empty

                    my_dir = hedge.getDirection()
                    prev_dir = hedge.previous.getDirection()

                    possible_dirs = ['l', 'r']
                    if my_dir == 'l' or prev_dir == 'r':
                        possible_dirs.remove('l')
                    if my_dir == 'r' or prev_dir == 'l':
                        possible_dirs.remove('r')

                    print("I'm hedge {}, my possible dirs are: {}".format(hedge, possible_dirs))

                    if 'l' in possible_dirs and hedge.origin.x > sweeping_line.min_item()[0]:

                        left_hedge = sweeping_line.floor_item(hedge.origin.x - 1)[1]

                        # going left -> hedge must go down
                        if left_hedge.getDirection() == 'd':
                            print("I'm hedge {}, and i'm actually going LEFT".format(hedge))

                            old_vert = hedge.origin

                            if left_hedge.origin.y == hedge.origin.y:
                                new_v_hedge = left_hedge.previous
                                new_vert = left_hedge.origin
                            elif left_hedge.next.origin.y == hedge.origin.y:
                                new_v_hedge = left_hedge
                                new_vert = left_hedge.next.origin
                            else:
                                coords = left_hedge.findIntersection(old_vert)

                                if coords in self.vertexSet:
                                    break

                                new_vert = self.divideHedge(left_hedge, coords, 'd')
                                new_v_hedge = left_hedge.previous

                            self.joinHedges(hedge, new_v_hedge, old_vert, new_vert, 'l')

                    if 'r' in possible_dirs and hedge.origin.x < sweeping_line.max_item()[0]:

                        right_hedge = sweeping_line.ceiling_item(hedge.origin.x + 1)[1]

                        # going right -> hedge must go up
                        if right_hedge.getDirection() == 'u':

                            print("I'm hedge {}, and i'm actually going RIGHT".format(hedge))

                            old_vert = hedge.origin
                            coords = right_hedge.findIntersection(old_vert)

                            if coords in self.vertexSet:
                                break

                            new_vert = self.divideHedge(right_hedge, coords, 'u')
                            new_v_hedge = right_hedge.next

                            self.joinHedges(hedge, new_v_hedge, old_vert, new_vert, 'r')

            for h in to_be_removed:
                print("i'm removing hedge", h)
                sweeping_line.remove(h)

    def verticalSweep(self):

        sweeping_line = AVLTree()

        for l in self.eventList:

            print("List on", l[0].origin.x, "contains events: ", l)

            # one cycle to add hedges
            print(l)
            for hedge in l:
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()

                if my_dir == 'l':

                    # direction of sweeping line -> add vertex
                    print("hedge {} is trying to insert {}".format(hedge, hedge.origin.y))

                    try:
                        value = sweeping_line.get_value(hedge.origin.y)
                        value.append(hedge)
                    except KeyError:
                        sweeping_line.insert(hedge.origin.y, [hedge])

                elif prev_dir == 'r':

                    print("hedge {} is trying to insert {}".format(hedge, hedge.previous.origin.y))

                    try:
                        value = sweeping_line.get_value(hedge.previous.origin.y)
                        value.append(hedge.previous)
                    except KeyError:
                        sweeping_line.insert(hedge.previous.origin.y, [hedge.previous])

            to_be_removed = []

            # another to close/expand them
            for hedge in l:
                print("Sweeping Line :", sweeping_line, "on x:", hedge.origin.x, "on y:,", hedge.origin.y, "and event", hedge)
                my_dir = hedge.getDirection()
                prev_dir = hedge.previous.getDirection()

                # close
                if my_dir == 'r':
                    print("hedge {} is trying to remove {}".format(hedge, hedge.origin.y))

                    to_be_removed.append(hedge.origin.y)

                elif prev_dir == 'l':
                    print("hedge {} is trying to remove {}".format(hedge, hedge.previous.origin.y))

                    to_be_removed.append(hedge.previous.origin.y)

                print("Sweeping before expanding/after closing:", sweeping_line)

            # another cycle to expand hedges
            for hedge in l:
                if not sweeping_line.is_empty():  # only try to expand if sweeping line is not empty

                    my_dir = hedge.getDirection()
                    prev_dir = hedge.previous.getDirection()

                    possible_dirs = ['u', 'd']
                    if my_dir == 'u' or prev_dir == 'd':
                        possible_dirs.remove('u')
                    if my_dir == 'd' or prev_dir == 'u':
                        possible_dirs.remove('d')

                    # going up -> hedge must go left
                    # going down -> hedge must go right
                    print (hedge, "Can go to", possible_dirs)

                    if 'd' in possible_dirs and hedge.origin.y > sweeping_line.min_item()[0]:
                        down_hedge = sweeping_line.floor_item(hedge.origin.y - 1)[1][-1]

                        tmp_hedge = hedge
                        while True:

                            down_hedge = sweeping_line.floor_item(hedge.origin.y - 1)[1][0]

                            print("I {} am trying to go down into {}".format(hedge, down_hedge))

                            # going down -> hedge must go right
                            # hedges have to be in the same face
                            if down_hedge.getDirection() == 'r' and down_hedge.incidentFace == hedge.incidentFace:
                                print("I'm hedge {}, and i'm actually going DOWN".format(hedge))

                                old_vert = hedge.origin

                                if down_hedge.next.origin.x == hedge.origin.x:
                                    print("%%%%%Case one%%%%%")
                                    print("uh", down_hedge, "h", hedge)
                                    new_h_hedge = down_hedge
                                    new_vert = down_hedge.next.origin
                                else:
                                    coords = down_hedge.findIntersection(old_vert)

                                    new_vert = self.divideHedge(down_hedge, coords, 'r')
                                    new_h_hedge = down_hedge.next

                                self.joinHedges(hedge, new_h_hedge, old_vert, new_vert, 'd')

                                hedge = down_hedge.twin

                                if hedge.incidentFace == self.infiniteFace:
                                    break
                            else:
                                break

                        hedge = tmp_hedge

                    if 'u' in possible_dirs and hedge.origin.y < sweeping_line.max_item()[0]:
                        up_hedge = sweeping_line.ceiling_item(hedge.origin.y + 1)[1][0]

                        tmp_hedge = hedge
                        while True:

                            # if len(sweeping_line.ceiling_item(hedge.origin.y + 1)[1]) == 1:
                            #     up_hedge = sweeping_line.ceiling_item(hedge.origin.y + 1)[1][0]
                            # else:
                            up_hedge = sweeping_line.ceiling_item(hedge.origin.y + 1)[1][-1]

                            print("I {} am trying to go up into {}".format(hedge, up_hedge))

                            # going up -> hedge must go left
                            # hedges have to be in the same face
                            if up_hedge.getDirection() == 'l' and up_hedge.incidentFace == hedge.incidentFace:
                                print("I'm hedge {}, and i'm actually going UP".format(hedge))

                                old_vert = hedge.origin
                                if up_hedge.next.origin.x == hedge.origin.x:
                                    print("%%%%%Case one%%%%%")
                                    print("uh", up_hedge, "h", hedge)
                                    new_h_hedge = up_hedge
                                    new_vert = up_hedge.next.origin
                                elif up_hedge.origin.x == hedge.origin.x:
                                    print("%%%%%%Case two%%%%%")
                                    print("uh", up_hedge, "h", hedge)
                                    new_h_hedge = up_hedge.previous
                                    new_vert = up_hedge.origin
                                else:
                                    coords = up_hedge.findIntersection(old_vert)

                                    new_vert = self.divideHedge(up_hedge, coords, 'l')
                                    new_h_hedge = up_hedge.previous

                                self.joinHedges(hedge, new_h_hedge, old_vert, new_vert, 'u')

                                hedge = up_hedge.twin.next

                                if hedge.incidentFace == self.infiniteFace:
                                    break
                            else:
                                break

                        hedge = tmp_hedge

            for h in to_be_removed:
                print("i'm removing hedge", h)

                if len(sweeping_line.get_value(h)) == 1:
                    sweeping_line.remove(h)
                else:
                    del sweeping_line.get_value(h)[0]
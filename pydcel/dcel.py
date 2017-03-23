import numpy as np
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
            print "illegal element type"

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
                print "this edge has a problem with its twin:",
                print e

    def remove_vertex(self, vertex):
        """Experimental!"""
        # remove this vertex from the DCEL and keep the topo right. Assumes no dangling edges.
        e_0 = vertex.incidentEdge
        # print "removing ",
        # print vertex
        # print "with incidentEdge",
        # print e_0
        
        # we don't want to come near the infiniteFace
        for e in e_0.wind():
            # raw_input()
            print e, e.twin, e.incidentFace
            if e.incidentFace == self.infiniteFace:
                print "refusing to remove vertex incident to infiniteFace..."
                return

        # we also don't want to create any dangling edges
        for e in e_0.wind():
            if e.previous == e.twin.next.twin:
                print "refusing to remove this vertex because it will create dangling edge(s)"
                return
            for e_neighbor in e.next.wind():
                if e_neighbor.previous == e_neighbor.twin.next.twin:
                    print "refusing to remove this vertex because it might cause dangling edge(s) in future"
                    return

        # FIXME: what to do if we are about to create a hole...?
        
        #This face we like so we keep it.
        nice_face = e_0.incidentFace
        
        toRemove = [vertex]

        current_edge = e_0.twin
        if current_edge.incidentFace != nice_face:
            toRemove.append(current_edge.incidentFace)
        # update all face references to nice face
        while current_edge != e_0.previous:
            # loop backwards over face that must be removed and set incidentface fields to nice face
            while current_edge.origin != vertex:
                current_edge = current_edge.previous
                # if current_edge == None: return
                current_edge.incidentFace = nice_face

            current_edge = current_edge.twin
            # this face must be gone
            if current_edge.incidentFace != nice_face:
                toRemove.append(current_edge.incidentFace)

        # update prev and next fields
        edges = [e for e in e_0.wind()]
        for e in edges:
            e.next.previous = e.twin.previous
            e.twin.previous.next = e.next
            e.twin.origin.incidentEdge = e.next
            toRemove.append(e)
            toRemove.append(e.twin)

        # now we can finally get rid of this stuff
        nice_face.outerComponent = e_0.next
        for element in toRemove:
            self.remove(element)
            
    def separateHedges(self):
        #separates vertical and horizontal edges
        #the ones chosen didnt had the incident face being inf
        for i in self.hedgeList:
            if (i.incidentFace.identifier  != "i"):
                self.eventList.append(i)
        self.eventList = sorted(self.eventList, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
        
        
    def horizontalSweep(self):
        for i in self.vertexList:
            i.checkReflex()
        sweepingLine = []
        
        for i in self.eventList:
            print ("Checking ", i)
            myDir = i.getDirection()
            prevDir = i.previous.getDirection()
            # start
            if myDir == 'd':
                # direction da sweeping line -> add vertex
                sweepingLine.append(i)
            elif prevDir == 'u':
                sweepingLine.append(i.previous)
                
            # close
            if myDir == 'u':
                sweepingLine.remove(i)
            elif prevDir == 'd':
                sweepingLine.remove(i.previous)
            # expand
            if i.origin.isReflex:
                possibleDirs = ['l', 'r']
                if myDir == 'l' or prevDir == 'r':
                    possibleDirs.remove('l')
                if myDir == 'r' or prevDir == 'l':
                    possibleDirs.remove('r')
                print("Can try to expand to : ", possibleDirs)
            print ("Sweeping is now ", sweepingLine)
                    
                    
                #esquerda -> edge tem de descer
                #direita -> edge tem de subir

            
            
                
            
            
            
def orderSweep(l):
    l = sorted(l, key = lambda x: (x.origin.y, x.origin.x), reverse = True)
    return l

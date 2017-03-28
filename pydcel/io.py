from .dcel import vertex, hedge, face, DCEL

def ply2datadict(infile):
    """collect vertex coordinates and normals from input file"""
    datadict = {}
    with open(infile) as f:
        vertexcount = None
        holecount = None
        flag_grid = False
        
        line = f.readline()

        datadict['coords'] = []
        datadict['faces'] = []
        
        if int(line) == 1:
            flag_grid = True
        vertexcount = int(f.readline())
        for i in range(vertexcount):
            line = f.readline()
            x, y = line.split()
            datadict['coords'].append([float(x), float(y)])
        vertex_ids = [x for x in range(int(vertexcount))]
        datadict['faces'].append(vertex_ids)
            
        holecount = int(f.readline())
        if holecount != 0:
            for i in range(holecount):
                hole_vertex_count = int(f.readline())
                vertexcount = vertexcount + hole_vertex_count
                for j in range(hole_vertex_count):
                    line = f.readline()
                    x, y = line.split()
                    datadict['coords'].append([float(x), float(y)])
                vertex_ids = [x for x in range(vertexcount - hole_vertex_count, vertexcount)]
                datadict['faces'].append(vertex_ids)
    return datadict


def datadict2dcel(datadict):
    print (datadict)
    # assume ccw vertex order
    hedges = {}  # he_id: (v_origin, v_end), f, nextedge, prevedge
    vertices = {}  # v_id: (e0,...,en) i.e. the edges originating from this v

    D = DCEL()
    int_face = D.createFace()
    inf_face = D.createInfFace()
    offset = 0
    first_twin = len(datadict['faces'][0])
    
    for coord in datadict['coords']:
        D.createVertex(coord[0], coord[1])
    for face in datadict['faces']:
        n_vertex_in_face = len(face)
        # create hedges incident to the interior face
        for hedge in face:
            new_hedge = D.createHedge()
        # create twin hedges incident to infinite face
        for hedge in face:
            new_hedge_twin = D.createHedge()
        for index in range(len(face)):
    
            D.hedgeList[offset + index].setTopology(D.vertexList[face[index]], D.hedgeList[offset + n_vertex_in_face + index],int_face, D.hedgeList[offset + (index + 1)%n_vertex_in_face], D.hedgeList[offset + (index - 1)%n_vertex_in_face])

            D.vertexList[face[index]].incidentEdge = D.hedgeList[offset + index]
            
            D.hedgeList[offset + n_vertex_in_face + index].setTopology(D.vertexList[face[(index + 1)%n_vertex_in_face]], D.hedgeList[offset + index], inf_face, D.hedgeList[offset + n_vertex_in_face + (index - 1)%n_vertex_in_face], D.hedgeList[offset + n_vertex_in_face + (index + 1)%n_vertex_in_face])
            
        offset += 2 * n_vertex_in_face
    int_face.setTopology(D.hedgeList[0])
    inf_face.setTopology(D.hedgeList[first_twin])
    
    D.separateHedges()
    D.horizontalSweep()
    
    return D


def ply2dcel(infile):
    datadict = ply2datadict(infile)
    return datadict2dcel(datadict)

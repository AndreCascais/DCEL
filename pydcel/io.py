from . import dcel

GRID_PARTITION_FLAG = True


def ply2datadict(infile):
    """collect vertex coordinates from input file"""
    datadict = {'coords': [], 'faces': []}

    with open(infile) as f:
        line = f.readline()

        if int(line) == 0:
            global GRID_PARTITION_FLAG
            GRID_PARTITION_FLAG = True

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
                vertexcount += hole_vertex_count
                for j in range(hole_vertex_count):
                    line = f.readline()
                    x, y = line.split()
                    datadict['coords'].append([float(x), float(y)])
                vertex_ids = [x for x in range(vertexcount - hole_vertex_count, vertexcount)]
                datadict['faces'].append(vertex_ids)
    return datadict


def datadict2dcel(datadict):

    polygon = dcel.DCEL()
    int_face = polygon.createFace()
    inf_face = polygon.createInfFace()

    offset = 0
    first_twin = len(datadict['faces'][0])

    for coord in datadict['coords']:
        polygon.createVertex(coord[0], coord[1])

    for face in datadict['faces']:
        n_vertex_in_face = len(face)

        # create hedges incident to the interior face
        for _ in face:
            polygon.createHedge()
        # create twin hedges incident to infinite face
        for _ in face:
            polygon.createHedge()

        for index in range(len(face)):

            polygon.hedgeList[offset + index].setTopology(polygon.vertexList[face[index]], polygon.hedgeList[offset + n_vertex_in_face + index], int_face, polygon.hedgeList[offset + (index + 1) % n_vertex_in_face], polygon.hedgeList[offset + (index - 1) % n_vertex_in_face])

            polygon.vertexList[face[index]].incidentEdge = polygon.hedgeList[offset + index]

            polygon.hedgeList[offset + n_vertex_in_face + index].setTopology(polygon.vertexList[face[(index + 1) % n_vertex_in_face]], polygon.hedgeList[offset + index], inf_face, polygon.hedgeList[offset + n_vertex_in_face + (index - 1) % n_vertex_in_face], polygon.hedgeList[offset + n_vertex_in_face + (index + 1) % n_vertex_in_face])

        offset += 2 * n_vertex_in_face

    int_face.setTopology(polygon.hedgeList[0])
    inf_face.setTopology(polygon.hedgeList[first_twin])

    return polygon


def ply2dcel(infile):
    datadict = ply2datadict(infile)
    return datadict2dcel(datadict)

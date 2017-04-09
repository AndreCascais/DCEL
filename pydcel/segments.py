class Segment:

    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def intersectsWith(self, seg):
        if self.src == seg.src or self.src == seg.dest or self.dest == seg.src or self.dest == seg.dest:  # Intersection will be a single point
            return False

        o1 = orientation(self.src, self.dest, seg.src)
        o2 = orientation(self.src, self.dest, seg.dest)
        o3 = orientation(seg.src, seg.dest, self.src)
        o4 = orientation(seg.src, seg.dest, self.dest)

        if o1 != o2 and o3 != o4 and 0 not in [o1, o2, o3, o4]:  # 0 is for colinear, which we want to keep !
            return True

        return False


class SegmentList:

    def __init__(self):
        self.list = []

    def addSegment(self, seg):
        self.list.append(seg)

    def canIntersect(self, seg):
        for i in self.list:
            if i.intersectsWith(seg):
                return True
        return False


def orientation(p1, p2, p3):
    res = ((p2.y - p1.y) * (p3.x - p1.x)) - ((p3.y - p1.y) * (p2.x - p1.x))
    if (res == 0):
        return 0
    elif (res > 0):
        return 1
    else:
        return -1

from __future__ import print_function

import math

from .interface_draw import draw
from .vector import vec2

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

HELP = """
q - quit
h - print help message
p - print dcel

e - iterate through next hedges
b - iterate through previous hedges
t - iterate through twins
v - iterate through vertices
f - iterate through faces
"""


def print_help():
    print(HELP)


class dcelVis(Tk):
    def __init__(self, dcel):
        Tk.__init__(self)
        self.sizex = 1000
        self.sizey = 1000
        self.window_diagonal = math.sqrt(self.sizex ** 2 + self.sizey ** 2)
        self.title("DCELvis")
        self.resizable(0, 0)

        self.bind('<Motion>', self.coords)

        self.bind('q', self.exit)
        self.bind('h', print_help)
        self.bind('p', self.print_dcel)

        self.bind('e', self.iteratehedge)
        self.bind('v', self.iteratevertex)
        self.bind('f', self.iterateface)
        self.bind('t', self.iteratetwin)
        self.bind('b', self.iterateprev)
        self.canvas = Canvas(self, bg="white", width=self.sizex, height=self.sizey)
        self.canvas.pack()

        self.coordstext = self.canvas.create_text(self.sizex, self.sizey, anchor='se', text='')
        self.info_text = self.canvas.create_text(10, self.sizey, anchor='sw', text='')

        self.tx = 0
        self.ty = 0

        self.highlight_cache = []
        self.bgdcel_cache = []

        self.draw = draw(self)

        self.D = None
        self.bind_dcel(dcel)
        self.hedge = dcel.hedgeList[-1].previous

    def coords(self, event):
        s = str(self.t_(event.x, event.y))
        self.canvas.itemconfig(self.info_text, text=s)

    def t(self, x, y):
        """transform data coordinates to screen coordinates"""
        x = (x * self.scale) + self.tx
        y = self.sizey - ((y * self.scale) + self.ty)
        return x, y

    def t_(self, x, y):
        """transform screen coordinates to data coordinates"""
        x = (x - self.tx) / self.scale
        y = (self.sizey - y - self.ty) / self.scale
        return int(round(x)), int(round(y))

    def print_dcel(self):
        print(self.D)

    def bind_dcel(self, dcel):
        minx = maxx = dcel.vertexList[0].x
        miny = maxy = dcel.vertexList[0].y
        for v in dcel.vertexList[1:]:
            if v.x < minx:
                minx = v.x
            if v.y < miny:
                miny = v.y
            if v.x > maxx:
                maxx = v.x
            if v.y > maxy:
                maxy = v.y

        d_x = maxx - minx
        d_y = maxy - miny
        c_x = minx + d_x / 2
        c_y = miny + d_y / 2

        if d_x > d_y:
            self.scale = (self.sizex * 0.8) / d_x
        else:
            self.scale = (self.sizey * 0.8) / d_y

        self.tx = self.sizex / 2 - c_x * self.scale
        self.ty = self.sizey / 2 - c_y * self.scale

        self.D = dcel

        self.draw_dcel()

    def draw_dcel(self):
        self.draw.deleteItems(self.bgdcel_cache)
        self.draw_dcel_faces()
        self.draw_dcel_hedges()
        self.draw_dcel_vertices()

        self.hedge_it = self.type_iterator('hedge')
        self.face_it = self.type_iterator('face')
        self.vertex_it = self.type_iterator('vertex')

    def iteratehedge(self, event):
        try:
            next(self.hedge_it)
        except StopIteration:
            self.hedge_it = self.type_iterator('hedge')
            next(self.hedge_it)

    def iterateface(self, event):
        try:
            next(self.face_it)
        except StopIteration:
            self.face_it = self.type_iterator('face')
            next(self.face_it)

    def iteratevertex(self, event):
        try:
            next(self.vertex_it)
        except StopIteration:
            self.vertex_it = self.type_iterator('vertex')
            next(self.vertex_it)

    def iteratetwin(self, event):
        try:
            next(self.hedge_it)
        except StopIteration:
            self.hedge_it = self.type_iterator('twin')
            next(self.hedge_it)

    def iterateprev(self, event):
        try:
            next(self.hedge_it)
        except StopIteration:
            self.hedge_it = self.type_iterator('prev')
            next(self.hedge_it)

    def type_iterator(self, q):
        if q == 'hedge':
            self.hedge = self.hedge.next
            yield self.explain_hedge(self.hedge)
        elif q == 'face':
            for e in self.D.faceList:
                yield self.explain_face(e)
        elif q == 'vertex':
            for e in self.D.vertexList:
                yield self.explain_vertex(e)
        elif q == 'twin':
            self.hedge = self.hedge.twin
            yield self.explain_hedge(self.hedge)
        elif q == 'prev':
            self.hedge = self.hedge.previous
            yield self.explain_hedge(self.hedge)

    def explain_hedge(self, e):
        print("I'm on hedge {} in face {}".format(e, e.incidentFace))
        self.draw.deleteItems(self.highlight_cache)

        i1 = self.draw_dcel_face(e.incidentFace, fill='#ffc0bf', outline='')
        i4 = self.draw_dcel_vertex(e.origin, size=7, fill='red', outline='')
        i2 = self.draw_dcel_hedge(e.next, arrow=LAST, arrowshape=(7, 6, 2), width=2, fill='#1a740c')
        i3 = self.draw_dcel_hedge(e.previous, arrow=LAST, arrowshape=(7, 6, 2), width=2, fill='#0d4174')
        i5 = self.draw_dcel_hedge(e, arrow=LAST, arrowshape=(7, 6, 2), width=3, fill='red')
        i6 = self.draw_dcel_hedge(e.twin, arrow=LAST, arrowshape=(7, 6, 2), width=3, fill='orange')

        self.highlight_cache = [i1, i2, i3, i4, i5, i6]

    def explain_vertex(self, v):
        print(v)

        self.draw.deleteItems(self.highlight_cache)

        i1 = self.draw_dcel_vertex(v, size=7, fill='red', outline='')
        i2 = self.draw_dcel_hedge(v.incidentEdge, arrow=LAST, arrowshape=(7, 6, 2), width=2, fill='red')

        self.highlight_cache = [i1, i2]

    def explain_face(self, f):
        print(f)
        self.draw.deleteItems(self.highlight_cache)

        i1 = self.draw_dcel_face(f, fill='#ffc0bf', outline='')
        i2 = self.draw_dcel_hedge(f.outerComponent, arrow=LAST, arrowshape=(7, 6, 2), width=3, fill='red')

        self.highlight_cache = [i1, i2]

    def draw_dcel_vertices(self):
        for v in self.D.vertexList:
            self.bgdcel_cache.append(self.draw_dcel_vertex(v))

    def draw_dcel_vertex(self, v, **options):
        if options == {}:
            options = {'size': 5, 'fill': 'blue', 'outline': ''}

        return self.draw.point(v.x, v.y, **options)

    def draw_dcel_hedges(self):
        for e in self.D.hedgeList:
            self.bgdcel_cache.append(self.draw_dcel_hedge(e))

    def draw_dcel_hedge(self, e, **options):
        if options == {}:
            options = {'arrow': LAST, 'arrowshape': (7, 6, 2), 'fill': '#444444'}

        offset = .02
        sx, sy = e.origin.x, e.origin.y
        ex, ey = e.twin.origin.x, e.twin.origin.y
        vx, vy = ex - sx, ey - sy
        v = vec2(vx, vy)
        v_ = v.orthogonal_l() * offset

        v -= v.normalized() * .25
        ex, ey = sx + v.x, sy + v.y

        return self.draw.edge((sx + v_.x, sy + v_.y), (ex + v_.x, ey + v_.y), **options)

    def draw_dcel_faces(self):
        for f in self.D.faceList:
            self.bgdcel_cache.append(self.draw_dcel_face(f))

    def draw_dcel_face(self, f, **options):
        if f == self.D.infiniteFace:
            print('Im not drawing infiniteFace')
            return

        if options == {}:
            options = {'fill': '#eeeeee', 'outline': ''}
        vlist = [(v.x, v.y) for v in f.loopOuterVertices()]
        return self.draw.polygon(vlist, **options)

    def exit(self, event):
        print("bye bye.")
        self.quit()
        self.destroy()

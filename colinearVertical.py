import pydcel

d = pydcel.io.ply2dcel('sampledata/colinearVertical.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

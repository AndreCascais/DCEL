import pydcel

d = pydcel.io.ply2dcel('sampledata/colinear.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

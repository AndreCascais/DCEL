import pydcel

d = pydcel.io.ply2dcel('sampledata/ricTestColinear.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

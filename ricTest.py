import pydcel

d = pydcel.io.ply2dcel('sampledata/ricTest.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

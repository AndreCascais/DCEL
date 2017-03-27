import pydcel

d = pydcel.io.ply2dcel('sampledata/hGrid.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

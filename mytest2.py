import pydcel.io

d = pydcel.io.ply2dcel('sampledata/HGrid.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

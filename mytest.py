import pydcel

d = pydcel.io.ply2dcel('sampledata/mygrid.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

import pydcel

d = pydcel.io.ply2dcel('sampledata/squares.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

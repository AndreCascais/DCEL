import pydcel

d = pydcel.io.ply2dcel('sampledata/mygrid2.ply')

gui = pydcel.dcelVis(d)
gui.mainloop()

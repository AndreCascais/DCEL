import pydcel

d = pydcel.io.ply2dcel('sampledata/squares.ply')

gui = pydcel.dcelVis(d)
# change in dcel
#gui.draw_dcel()
#gui.update()
#sleep(x)
#
#
gui.mainloop()

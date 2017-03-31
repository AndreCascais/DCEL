import pydcel.io

file_list = ['sampledata/colinear.ply', 'sampledata/colinearVertical.ply', 'sampledata/hGrid.ply',
             'sampledata/lTest.ply', 'sampledata/mygrid.ply', 'sampledata/mygrid2.ply', 'sampledata/ricTest.py',
             'sampledata/ricTestColinear.py', 'sampledata/squares.py', 'sampledata/simplegeom.py']


for f in file_list:
    print(f)
print("")

chosen_file = input("which file do you want: ",)

d = pydcel.io.ply2dcel(chosen_file)

# change in dcel
# gui.draw_dcel()
# gui.update()
# sleep(x)

gui = pydcel.dcelVis(d)
gui.mainloop()

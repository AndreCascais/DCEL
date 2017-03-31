import pydcel
import sys

if len(sys.argv) == 2:
    chosen_file = sys.argv[1]

else:
    file_list = ['sampledata/colinear.ply', 'sampledata/colinearVertical.ply', 'sampledata/hGrid.ply',
                 'sampledata/lTest.ply', 'sampledata/mygrid.ply', 'sampledata/mygrid2.ply', 'sampledata/ricTest.ply',
                 'sampledata/ricTestColinear.ply', 'sampledata/squares.ply', 'sampledata/simplegeom.ply']

    for f in file_list:
        print(f)
    print("")

    chosen_file = input("which file do you want: ",)

d = pydcel.io.ply2dcel(chosen_file)
d.horizontalSweep()

d.separateHedges('h')
d.horizontalSweep()
d.renameFaces()
print ("Horizontal done")

# if pydcel.io.DAT_FLAG_DOE:
#     d.separateHedges('v')
#     d.verticalSweep()
#     d.renameFaces()

print ("Vertical done")

# change in dcel
# gui.draw_dcel()
# gui.update()
# sleep(x)

gui = pydcel.dcelVis(d)
gui.mainloop()

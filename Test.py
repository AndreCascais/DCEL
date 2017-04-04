import pydcel
import sys
import readline
from os import listdir
import numpy as np

try:
    input = raw_input
except NameError:
    pass

file_list = listdir("sampledata")

class SimpleCompleter(object):
    
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s 
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        
        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response

# Register our completer function
readline.set_completer(SimpleCompleter(file_list).complete)

# Use the tab key for completion
readline.parse_and_bind('tab: complete')


if len(sys.argv) == 2:
    chosen_file = sys.argv[1]

else:
    for f in file_list:
        print(f)
    print("")

    chosen_file = input("which file do you want: ",)
    
d = pydcel.io.ply2dcel("sampledata/" + str(chosen_file))
d.separateHedges('h')
d.hedgesToSegments()
d.horizontalSweep()
d.renameFaces()
print("-------------HORIZONTAL DONE------------")
if pydcel.io.GRID_PARTITION_FLAG:
    d.separateHedges('v')
    d.verticalSweep()
    d.renameFaces()

print("-------------VERTICAL DONE------------")
if (pydcel.io.VISIBILITY_FLAG):
    d.computeVertexVisibility()
    d.computeFaceVisibility()
    d.printMatrix()

GUI = pydcel.dcelVis(d)
GUI.mainloop()

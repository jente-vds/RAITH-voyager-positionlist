# Import the necessary modules
import numpy as np
import gdstk
import voyager as vyg

#Initiate an empty GDSII library and an empty positionlist, as well as the layer and datatype
lib = gdstk.Library()
pls = vyg.Positionlist('20mm2.wlo')
ld = {"layer":0, "datatype":1000}

# We wish to create an array of antennas, where we vary the pitch and size of the antennas
# We furthermore wih to pattern these in an array, where their position corresponds to their parameters
pitches = np.arange(1,5)
lengths = 0.1 * np.arange(3,8)
widths = 0.05 * np.arange(2,9,2)

# Let us define a function to add such an array of size 10x10 to a cell, depending on pitch, length, and width.
def arr(cell, pitch, length, width, layer=0, datatype=1000):
     pos = pitch * np.arange(-5,6)
     for x in pos:
             for y in pos:
                     cell.add(gdstk.rectangle((x-width/2,y-length/2), (x+width/2,y+length/2), layer=layer, datatype=datatype))

# Now we can start creating all of these
for pitch in pitches:
     for i, length in enumerate(lengths):
             for j, width in enumerate(widths):
                     # Create a cell
                     name = 'p{0}_l{1}_w{2}'.format(pitch, int(1e3*length), int(1e3*width))
                     cell = gdstk.Cell(name)
                     # Add the structures to the cell
                     arr(cell, pitch, length, width, **ld)
                     # Add the cell to the GDSII library
                     lib.add(cell)
                     # Add an entry containing said cell to the positionlist
                     position = (7.7 - 4*(pitch%2) + .200*j, 4.4 + (pitch>2)*4 - .200*i)
                     pls.add(cell, position)

# We can also add markers
for i, length in enumerate(lengths):
     name = 'length{}'.format(int(1e3*length))
     cell = gdstk.Cell(name)
     cell.add(*gdstk.text('length {}'.format(int(1e3*length)), size=20, position=(0,0)))
     pls.add(cell, (3.5, 4.4-0.200*i))
     pls.add(cell, (7.5, 4.4-0.200*i))
     pls.add(cell, (3.5, 8.4-0.200*i))
     pls.add(cell, (7.5, 8.4-0.200*i))

for i, width in enumerate(widths):
     name = 'width{}'.format(int(1e3*width))
     cell = gdstk.Cell(name)
     cell.add(*gdstk.text('width {}'.format(int(1e3*width)), size=20, position=(0,0)))
     pls.add(cell, (3.5, 4.4-0.200*i))
     pls.add(cell, (7.5, 4.4-0.200*i))
     pls.add(cell, (3.5, 8.4-0.200*i))
     pls.add(cell, (7.5, 8.4-0.200*i))

# Now of course, everything is ordered poorly. So let us change it such that those things near each other, will be written after one another
pls.shortSort()

# Let us also make sure that all the structres we write will be centered at the the writefield, and not in the corner, as the VOYAGER is apt to do.
pls.setArea(np.array([-100,-100,100,100]))

# Now let us check the ordering and the structures
pls.plot(order=True)

# Add a file
pls.assignFile('example_advanced.gds')
lib.write_gds('example_advanced.gds')
pls.write('example_advanced.pls')

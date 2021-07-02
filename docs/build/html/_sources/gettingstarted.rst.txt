###############
Getting Started
###############

****************************
First GDSII and Positionlist
****************************

Let's start by importing the modules, creating our first GDSII cell and initiating a Positionlist:

.. code-block:: python

   import gdstk
   import voyager as vyg

   # The GDSII file is called a library, which contains multiple cells.
   lib = gdstk.Library()
   # Define a layer and datatype.
   ld_0 = {"layer":0, "datatype":1000}
   ld_1 = {"layer":1, "datatype":1200}

   # Initiate a Positionlist using the 12x12mm wafermap
   pls = vyg.Positionlist("12x12mm.wlo")

   # Geometry must be placed in cells.
   cell_1 = gdstk.Cell("First_cell")
   cell_2 = gdstk.Cell("Second_cell")

   # Create the geometry (a single rectangle) in layer 0 and add it to the first cell.
   rect = gdstk.rectangle((0, 0), (2, 1), **ld_0)
   cell_1.add(rect)
   
   # Add the two cells to the positionlist.
   pls.add(cell_1, (3,3))
   pls.add(cell=cell_2, position=(3.2,3), layer=1, dosefactor=0.8)

   # Create another geometry (a circle) in layer 1 and add it to the second cell.
   circle = gdstk.ellipse((0,0), 5, **ld_1)
   cell_2.add(circle)

   # Print the current status of the positionlist.
   print(pls)


After importing the `gdstk` and `voyager` modules, we create a positionlist `pls` with a 12x12mm wafermap.
We add structures to the cells and we add those cells to the positionlist at the desired positions and patterning the desired layer(s).

Let us add some more structures and do manipulation on them.

.. code-block:: python

   # Add another Polygon to cell_2
   ellipse = gdstk.ellipse((5,0), [1,3], layer=3, datatype=1000)
   cell_2.add(ellipse)

   # Add the cell to the positionlist at another position, but this time with both layers
   pls.add(cell_2, (3.4,3), layer=[1,3])

   # Create a matrix copy of the second entry
   pls.matrixCopy(size=(3,2), row_vector=(0,3), column_vector=(6,0), dose_change=(lambda x: x*1.1), selection="ID == 2")

   # Review the positionlist
   pls.printout(['ID', 'Comment', 'U', 'V', 'Area', 'Layer', 'DoseFactor'])

   # We still miss an area entry. So let us update the areas
   pls.updateArea()

   # Review the positionlist again
   pls.printout(['ID', 'Comment', 'U', 'V', 'Area', 'Layer', 'DoseFactor'])

   # Write out the positionlist
   pls.write("example.pls")

Oops, something happened. Apparently we still have to assign a file to the positionlist. When you load the positionlist in the VOYAGER, it has to read the cells it wishes to write from a (GDSII) file. We will have to give it the path to said file, respective to :literal:`%UserRoot%GDSII\\`. Note that we are talking about a Windows path, which uses backslashes (:literal:`'\\'` in Python) as folder separation.
Furthermore, if you forget an area in your positionlist, you will also receive a warning before being able to write.

.. code-block:: python

   # Assign a file to the positionlist
   pls.assignFile("example.gds")

   # Let's review the postionlist first
   pls.plot(flatten=True)

   # Now we can save it all
   lib.write("example.gds")
   pls.write("example.pls")

We now place the GDSII file at location :literal:`%UserRoot%GDSII\\example.gds` and we load :literal:`example.pls` in the VOYAGER.

*****************
Advanced examples
*****************

Let us try another example, but this time a little more difficult. It will demonstrate why using :literal:`voyager-python` is so much easier and faster than using the VOYAGER itself to create positionlists.

.. code-block:: python

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

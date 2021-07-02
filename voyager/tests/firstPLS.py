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

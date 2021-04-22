##############################
Voyager-python's documentation
##############################

The RAITH VOYAGER is an electron beam lithography system. It takes an input file containing polygons, paths and shapes in order to write these structures on a sample. The most commonly used file is a GDSII file, with a :literal:`.gds` extension.

After importing a GDSII file in the VOYAGER, you have to create a positionlist (:literal:`.pls`). This is a list specifiying which cells of the GDSII to write at what location, with what dosefactor, what area of the cell, what layers, etc.
However, despite being able to perform certain bulk operations, this is still an extremely tenuous process, since each cell has to be loaded individually, values can not be changed in bulk, and in order to change parameters, you often have to rely on submenus. Furthermore, creating a positionlist is usually done behind the VOYAGER, decreasing uptime. The mindnumbing process that is creating a positionlist also gives a change of introducing human errors.

This Python package is meant to mitigate this and allow users to create positionlist from behind their own computer. The package is designed to work with gdstk, a python package for creating GDSII files (https://github.com/heitzmann/gdstk). It can also work with the deprecated package gdspy, however, its usage is not advised.

.. automodule:: voyager

.. toctree::
   :maxdepth: 3
   :caption: Table of Contents

   gettingstarted
   reference

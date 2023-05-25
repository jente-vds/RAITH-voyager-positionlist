# RAITH-voyager-positionlist
A python package to facilitate creating positionlists for RAITH VOYAGER systems. **WIP**

The VOYAGER e-beam lithography system from RAITH uses a positionlist to determine what cells from an input file to write where.  
This process oftentimes has to be performed manually in a GUI. For large sets of cells, this is highly inefficient.  
  
This package aims to mitigate this issue by allowing users to create their own positionlist, reducing overhead at the machine and limiting the time it takes to create a pocitionlist.

## Requirements
- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)
- [pandas](https://pandas.pydata.org/)
- [gdstk](https://github.com/heitzmann/gdstk) (preferred) or [gdspy](https://github.com/heitzmann/gdspy)

## Installation
python setup.py install

## Documentation
Full documentation can be found [here](https://jente-vds.github.io/RAITH-voyager-positionlist/).

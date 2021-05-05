import numpy as np
import pandas as pd
from ._helpers import rounderupper

class WA:
    """
    Helper class for WorkingAreas.

    Parameters
    ----------
    name : string
        The name of the cell for which the following working areas are created.
    working_area : list or 1d numpy array of len 4
        The working area to add to the cell.

    Attributes
    ----------
    wa_list : list
        list containing all the different working areas.
    name : string
        The name of the cell to which the working areas pertain.
    """
    __slots__ = ['wa_list', 'name', 'active']
    def __init__(self, name, working_area):
        self.wa_list = [np.array(working_area)]
        self.name = name
        self.active = 0
    
    def __str__(self):
        string = 40*"=\n" + self.name + ", activeWA = " + self.active  + "\n"+ 40*'-'  + "\n"
        for i, wa in enumerate(self.wa_list):
            string += '{:2d} | {:8.3f} {:8.3f} {:8.3f} {:8.3f}\n'.format(i, *wa)
        string += 40*'=' + "\n"
        return string

    def __len__(self):
        return len(self.wa_list)

    def add(self, working_area):
        """
        Add a working area to the cell.

        Parameters
        ----------
        working_area : list or 1D numpy array of len 4
            The working area to add to the cell.
        """
        self.wa_list.append(np.array(working_area))
        self.active = len(self.wa_list)-1

    def delete(self, num):
        """ 
        Deletes the appropriate working area from the cell.

        Parameters
        ----------
        num : int
            The number of the working area to be deleted
        """
        del self.wa_list[num]
        if self.active == num:
            self.active = len(self.wa_list)-1

class WorkingAreas:
    """
    Registry for the working areas for different cells
    
    Parameters
    ----------
    unit : float
        This value has to equal the database unit used in the corresponding GDSII file

    Attributes
    ----------
    cells : dictionary
        Dictionary containing the objects storing the working areas
    unit : float
        The precision defined for this .wor file.
    """
    def __init__(self, unit=1e-9):
        self.cells = {}
        self.unit = unit
    
    def __str__(self):
        for i in self.cells.values():
            print(i)

    def __len__(self):
        return len(self.cells)

    def add(self, cell, working_area):
        """
        Add or update a working area for a specific cell.

        Parameters
        ----------
        cell : gdstk.Cell, gdspy.Cell, or string
            The cell, or its name, for which you wish to add a working area
        working_area : list or numpy array of length 4
            The working area to add to the cell ([left_boundary, bottom_boundary, right_boundary, top_boundary]).
        """
        if not isinstance(cell, str):
            name = cell.name
        else:
            name = cell
        working_area = np.reshape(working_area, 4)
        if name in self.cells:
            self.cells[name].add(working_area)
        else:
            self.cells[name] = WA(name, working_area)

    def delete(self, cell, num=None):
        """Delete a cell from the list.

        Parameters
        ----------
        cell : gdspy.Cell, gdstk.Cell, or string
            The cell, or its name, for which to delete the working areas.
        num : int
            The number of the working area to remove. If None, removes all working areas from said cell.
        """
        if isinstance(cell, str):
            name = cell
        else:
            name = cell.name
        if num == None or len(self.cells[name])==1:
            del self.cells[name]
        else:
            self.cells[name].delete(num)

    def setActive(self, cell, num):
        """
        Set a specific working area as the active one for a cell.

        Parameters
        ----------
        cell : gdstk.Cell, gdspy.Cell, or string
            The cell or its name for which you wish to set the active working area
        num: int
            The number of the working area that you wish to set as active.
        """
        if isinstance(cell, str):
            name = cell
        else:
            name = cell.name
        if 0 <= num < len(self.cells[name]):
            self.cells[name].active = num
        else:
            raise ValueError("This working area corresponding to this num does not exist.")

    def write(self, filename):
        """Write out the working areas to a .wor file.

        Parameters
        ----------
        filename : string
            The filename for the .wor file (e.g. example.wor)
        """
        open(filename, 'w').close()
        with open(filename, 'a') as f:
            for i in sorted(self.cells):
                 select = self.cells[i]
                 wa = rounderupper(select.wa_list[select.active]*1e-6/self.unit)
                 f.write("[{0}]\nWorkingArea={1}\nActiveWA={2}\n".format(select.name, ','.join(str(wa).split()).strip('[]'), select.active))
                 for j, arr in enumerate(select.wa_list):
                     f.write("WorkingArea{0}={1}\n".format(j, np.array2string(arr, precision=3, separator=',').strip('[]')))


def read_wor(self, filename):
    """Read an existing working area (.wor) file into a voyager.wor.WorkingAreas instance.

    Parameters
    ----------
    filename : string
        The file to read"""
    wa =  WorkingAreas()
    with open(filename, "r") as f:
        text = f.read()
    begin = 0
    while text.find('[', begin) != -1:
        start = text.find('[', begin) + 1
        stop = text.find(']', begin)
        cell_name = text[start:stop]
        ActiveWA_start = text.find('ActiveWA=', begin) + len('ActiveWA=')
        ActiveWA_stop = text.find('\n', ActiveWA_start)
        ActiveWA = text[ActiveWA_start:ActiveWA_stop]
        WA_start = text.find('WorkingArea'+ActiveWA+'=', begin) + len('WorkingArea' + ActiveWA + '=')
        WA_stop = text.find('\n', WA_start)
        WA = text[WA_start:WA_stop].split(',')[0:4]
        wa.add(cell_name, np.array(WA, dtype=float))
        begin = stop + 1
    return wa


import numpy as np
import pandas as pd
class WorkingArea:
    """
    Registry for the working areas for different cells
    
    Parameters
    ----------
    precision : float
        The precision determines the amount of blocks in which the working area is divided.

    Attributes
    ----------
    df : pandas.DataFrame
        Pandas dataframe that contains the cell names and the corresponding working area boundaries.
    precision : float
        The precision defined for this .wor file.
    """
    def __init__(self, precision=1e-9):
        self.df = pd.DataFrame(columns=['cell_name','left','bottom','right','top'])
        self.precision = 1e-9
    
    def __str__(self):
        print(self.df) 

    def add(self, cell, working_area):
        """
        Add a working area for a specific cell.

        Parameters
        ----------
        cell : gdstk.Cell or gdspy.Cell
            The cell for which you wish to add a working area
        working_area : list or numpy array of length 4
            The working area to add to the cell ([left_boundary, bottom_boundary, right_boundary, top_boundary]).
        """
        working_area = np.reshape(working_area, 4)
        self.df = self.df.append({'cell_name':cell.name, 'left': working_area[0], 'bottom': working_area[1], 'right': working_area[2], 'top': working_area[3]}, ignore_index=True)

    def delete(self, cell):
        """Delete a cell from the list.

        Parameters
        ----------
        cell : gdspy.Cell or gdstk.Cell
            The cell for which to delete the working areas."""
        self.df.drop( self.df[self.df["cell_name"]==cell.name].index, inplace=True)

    def write(self, filename):
        """Write out the working areas to a .wor file.

        Parameters
        ----------
        filename : string
            The filename for the .wor file (e.g. example.wor)
        """
        open(filename, 'w').close()
        for i in range(len(self.df)):
            with open(filename, 'a') as f:
                f.write("[{0}]\nWorkingArea={1e-6*1[0]/self.precision:n},{1e-6*1[1]/self.precision:n},{1e-6*1[2]/self.precision:n},{1e-6*1[3]/self.precision:n}\nActiveWA=0\nWorkingArea0={1[0]:.3f},{1[1]:.3f},{1[2]:.3f},{1[3]:.3f},New\n".format(self.df.loc[i,0], self.df.loc[i,1:]))

def read_wor(self, filename):
    """Read an existing working area (.wor) file into a voyager.wor.WorkingArea instance.

    Parameters
    ----------
    filename : string
        The file to read"""
    wa =  WorkingArea()
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
        wa.df.append({'cell_name':cell_name, 'left': float(WA[0]), 'bottom': float(WA[1]), 'right': float(WA[2]), 'top': float(WA[3])}, ignore_index=True)
        begin = stop + 1
    return wa


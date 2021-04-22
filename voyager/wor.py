import numpy as np
import pandas as pd
class WorkingArea:
    """Registry for the working areas for different cells"""
    def __init__(self, precision=1e-9):
        self.df = pd.DataFrame(columns=['cell_name','left','bottom','right','top'])
        self.precision = 1e-9
    
    def __str__(self):
        print(self.df) 

    def add(self, cell, working_area):
        """Add a working area for a specific cell. The syntax is voyager.WorkingArea.add(cell, [left_boundary, bottom_boundary, right_boundary, top_boundary])."""
        working_area = np.reshape(working_area, 4)
        self.df = self.df.append({'cell_name':cell.name, 'left': working_area[0], 'bottom': working_area[1], 'right': working_area[2], 'top': working_area[3]}, ignore_index=True)

    def delete(self, cell):
        """Delete a cell from the list. The syntax is voyager.WorkingArea.del(cell)."""
        for count, i in enumerate(self.l):
            if i[0] == cell.name:
                del self.l[count]

    def write(self, filename):
        """Write out the working areas to a .wor file. The syntax is voyager.WorkingArea.write(filename)."""
        open(filename, 'w').close()
        for i in range(len(self.df)):
            with open(filename, 'a') as f:
                f.write("[{0}]\nWorkingArea={1e-6*1[0]/self.precision:n},{1e-6*1[1]/self.precision:n},{1e-6*1[2]/self.precision:n},{1e-6*1[3]/self.precision:n}\nActiveWA=0\nWorkingArea0={1[0]:.3f},{1[1]:.3f},{1[2]:.3f},{1[3]:.3f},New\n".format(self.df.loc[i,0], self.df.loc[i,1:]))

def read_wor(self, filename):
    """Read an existing working area (.wor) file into a voyager.WorkingArea instance."""
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


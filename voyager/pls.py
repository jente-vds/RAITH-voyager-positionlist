import numpy as np
import pandas as pd
import pkg_resources
if 'gdstk' in {pkg.key for pkg in pkg_resources.working_set}:
    import gdstk
    gdstk_key = True
elif 'gdspy' in {pkg.key for pkg in pkg_resources.working_set}:
    import gdspy
    gdstk_key = False
else:
    raise ImportError("Not gdstk, nor gdspy is installed. The package will not work.")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import random
from copy import copy
from ._helpers import pls_header, wafermaps, ALL_VOYAGER, colours, rounderupper, dist, distMatrix, entry_adder, polygon_key, func_n

class Positionlist:
    """A dataframe containing the data for a positionlist to be used in the RAITH VOYAGER.

    The voyager.Positionlist class generates a pandas DataFrame containing the positionlist, as well as generating a dictionary containing the cells you have added to the positionlist with a specified wafer layout (defaults to DEFAULT.wlo). Entries can be added and substracted with the add and delete commands. Specific parameters for a selection of entries (defaults to all entries) can be edited by builtin commands. For basic usage, this is unnecessary.
    
    Parameters
    ----------
    WaferLayout : string
        The wafer layout to be used for the positionlist. Has to be one of the possible wafermaps known by the VOYAGER (see wafermaps).
        
    Attributes
    ----------
    wlo : string
        The name of the wafer layout (with .wlo extension).
    df : pandas.DataFrame
        Pandas DataFrame storing all the necessary info for the VOYAGER, such as position, dose, cell name, etc.
    cells : dictionary
        Dictionary containing all the cells in the positionlist, with the cell names acting as keys.
    """
    def __init__(self, WaferLayout='DEFAULT.wlo'): 
        if WaferLayout not in wafermaps.keys():
            raise ValueError("This wafermap is not known in the voyager system. If it is, please notify package maintainer (j.vandersmissen@amolf.nl) to add said wafermap to the list.")
        self.wlo = WaferLayout
        self.df = pd.DataFrame(columns=["ID", "X", "Y", "Z", "R", "T", "U", "V", "W", "Attribute", "Template", "Comment", "Options", "Type", "Size-U", "Size-V", "Points-U", "Points-V", "Dir", "Avg", "Pos1", "Pos2", "Pos3", "Link", "File", "Layer", "Area", "DoseFactor", "Dwelltime", "Stepsize", "SplDwell", "SplStep", "CurveStep", "CurveDwell", "DotDwell", "FBMSArea", "FBMSLines", "SplDot", "Time", "Timestamp", "Method", "Dot"], dtype=object)
        self.cells = dict()

    def __len__(self):
        return len(self.df)

    def __str__(self):
        visible = ['ID', 'U', 'V', 'Comment', 'Layer', 'DoseFactor', 'StepsizeU', 'StepsizeV']
        return self.df[[i for i in self.df if i in visible]].to_string(index=False)

    def add(self, cell, position, layer=0, dosefactor=1):
        """
        Add an entry to the Positionlist.

        Parameters
        ----------
        cell : gdstk.Cell
            The cell to add to the positionlist.
        position : tuple
            The position at which to write the cell.
        layer : list of integers or integer
            The layer(s) of the cell that you wish to write.
        dosefactor : float
            The dosefactor with which you wish to multiply the base dose of this entry.
        """
        if gdstk_key:
            if not isinstance(cell, gdstk.Cell):
                raise TypeError("cell has to be an instance of gdstk.Cell")
        else:
            if not isinstance(cell, gdspy.Cell):
                raise TypeError("cell has to be an instance of gdspy.Cell")
        layer = np.array(layer).flatten()

        self.df = self.df.append(entry_adder(df=self.df, cell=cell, position=position, layer=layer, dosefactor=dosefactor), ignore_index=True)
        self.cells[cell.name] = cell

    def remove(self, selection='@ALL_VOYAGER'):
        """
        Removes the specified selection from the positionlist. WARNING: By default the entrie positionlist will be removed!

        Parameters
        ---------
        selection : string
            Query string with which you select the entries you wish to remove.

        Examples
        --------
        >>> Positonlist.remove("U < 5")
        >>> Positionlist.remove("Comment == 'wrong_cell'")
        """
        self.df.drop(index=self.df.query(selection).index, inplace=True)
        keys = self.cells.keys()
        for i in keys:
            if i not in self.df['Comment'].values:
                del self.cells[i]

    def assignFile(self, filename, selection = '@ALL_VOYAGER'):
        """
        Assign a gds file path to the Positionlist.

        This function assigns a gds file to the positionlist. Cells used in the positionlist will come from said file. This function has to be executed prior to writing the positionlist. The filename has to be where the gds file is stored on the VOYAGER PC, respective to the location %UserRoot%GDSII\\. Can also be executed on a selection of entries(defaults to all).

        Parameters
        ----------
        filename : string
            The path where to find the gds containing the cells used in the positionlist on the VOYAGER. Path relative to %UserRoot%GDSII\\.
        selection : string
            Query string with which you select the entries you wish to assign a file to.

        Examples
        --------
        >>> Positionlist.assignFile('project_1\\design_1.gds', selection = "Comment in {'cell1', 'cell3'}")
        >>> Positionlist.assignFile('project_1\\design_2.gds', selection = "Comment == 'cell2'")
        """
        self.df.loc[self.df.query(selection).index, 'File'] = '%UserRoot%GDSII\\' + filename 

    def writingArea(self, weighted=False):
        """This function will calculate the total area (in um^2) that you will write. If weighted is True, it will multiply the specific areas with their dose factor."""
        A = 0
        for i in range(len(self.df)):
            for j in self.cells[self.df.loc[i, 'Comment']].area(True).keys():
                if j[0] in self.df.loc[i,'Layer']:
                    A += self.cells[self.df.loc[i, 'Comment']].area(True)[j]*(1+weighted*(self.df.loc[i,'DoseFactor']-1))
        return A

    def writingTime(self, BeamCurrent = 5e-10, AreaDose = 150):
        """This function gives an approximation of the total writing time in s.

        Function approximating the writing time. It includes stage movement. Bear in mind that this is an approximation and the actual writing time will probably be larger. If necessary, it is possible to first attempt to reduce writing time by using the voyager.Positionlist.shortSort() algorithm.
        
        Parameters
        ----------
        BeamCurrent : float
            The beamcurrent you will use to write the structures (in A)
        AreaDose : float
            The base dose for your resist in (uC/cm^2)
        """ 
        # stitch_wait 1.5 s
        # drive_speed 10 mm in 5.5 s
        # polygon_nest 1 s
        # writing time = (DwellTime)*TotalArea/(StepSize*LineSpacing) = AreaDose*StepSize*LineSpacing/BeamCurrent*TotalArea/(StepSize*LineSpacing)
        # [s] = 1e-14*[uC/cm^2]*[um^2]/[A]
        s = self.df.loc[0,'U'] + self.df.loc[0,'V'] + np.sum(self.df['U'].diff()) + np.sum(self.df['V'].diff())
        time = 2.5 * len(self.df) + self.writingArea(weighted=True)*1e-14*AreaDose/BeamCurrent+s*5.5/10 #StitchWait + Polygonisation + WritingTime + StageMovement
        return time

    def shortSort(self, coolingRate = 2e-5):
        """Run a simulated annealing algorithm which will attempt to minimise the writing time of the voyager by finding the (approximate) shortest path between all the points."""
        DistMatrix = distMatrix(np.array(self.df[['U', 'V']]))
        path = random.sample(range(len(self)), len(self))
        T = 2*len(self)
        while T > 1:
            [i,j] = random.sample(range(len(self)), 2)
            newPath = path.copy()
            newPath[i], newPath[j] = newPath[j], newPath[i]
            oldDistance = dist(DistMatrix, path)
            newDistance = dist(DistMatrix, newPath)
            if np.exp( (oldDistance - newDistance)/T) > random.random():
                path = newPath.copy()
            T *= 1 - coolingRate
        self.df = self.df.reindex(path).reset_index(drop=True)

    def printout(self, attributes):
        """Prints out requested attributes of the Positionlist.

        More often than not, using print(voyager.Positionlist) should give you all the information you need. If you do have need of some more obscure functions such as setting the speed of FBMS, you can review it here.

        Parameters
        ----------
        attributes : list of strings
            List of the attributes you wish to print out

        Example
        -------
        >>> Positionlist.printout(['ID', 'Comment', 'U', 'V', 'FBMSArea', 'FBMSLines'])
        """
        print(self.df[attributes].to_string(index=False))

    def translate(self, translation, selection='@ALL_VOYAGER'):
        """Translate the selection (defaults to all) by a specific translation (in UV [mm]).

        Parameters
        ----------
        translation : tuple
            Vector with which you wish to translate the selected entries in UV (in mm).
        selection : string
            Query string with which you select the entries to translate
        """
        self.df.loc[self.df.query(selection).index, 'U'] += translation[0]
        self.df.loc[self.df.query(selection).index, 'V'] += translation[1]

    def rotate(self, angle, reference='origin', selection='@ALL_VOYAGER'):
        """Rotate the selected entries.

        Parameters
        ----------
        angle : float
            Angle by which to rotate the slected entries (in radians)
        reference : 'origin', 'corner',  'center', or tuple
            Define the point around which the selection will be rotated.
            Origin will rotate around the origin, corner around the bottom left corner of the selection, center around its center.
            When reference is a tuple, the selection will be rotated around that point.
        """
        if reference == 'corner':
            transx = np.min(self.df.loc[self.df.query(selection).index, 'U'])
            transy = np.min(self.df.loc[self.df.query(selection).index, 'V'])
        elif reference == 'center':
            transx = (np.min(self.df.loc[self.df.query(selection).index, 'U'])+np.max(self.df.loc[self.df.query(selection).index, 'U']))/2
            transy = (np.min(self.df.loc[self.df.query(selection).index, 'V'])+np.max(self.df.loc[self.df.query(selection).index, 'V']))/2
        elif reference == 'origin':
            transx = 0
            transy = 0
        elif isinstance(reference, tuple):
            transx = reference[0]
            transy = reference[1]
        else:
            raise ValueError("No valid reference point chosen. Available options are 'origin', 'corner', and 'center' or a tuple.")

        self.df.loc[self.df.query(selection).index, 'U'] -= transx
        self.df.loc[self.df.query(selection).index, 'V'] -= transy
        self.df.loc[self.df.query(selection).index, 'U'] = np.cos(angle)*self.df.loc[self.df.query(selection).index, 'U'] - np.sin(angle)*self.df.loc[self.df.query(selection).index, 'V']
        self.df.loc[self.df.query(selection).index, 'V'] = np.sin(angle)*self.df.loc[self.df.query(selection).index, 'U'] + np.cos(angle)*self.df.loc[self.df.query(selection).index, 'V']
        self.df.loc[self.df.query(selection).index, 'U'] += transx
        self.df.loc[self.df.query(selection).index, 'V'] += transy

    def matrixCopy(self, size, row_vector, column_vector, dose_change=(lambda x: x), selection='@ALL_VOYAGER'):
        """
        Create a matrix copy of the selection.

        Parameters
        ----------
        size : tuple
            Size of the matrix copy (rows, columns).
        row_vector : tuple
            Vector with which to displace each of the rows (in mm).
        column_vector : tuple
            Vector with which to displace each of the columns (in mm).
        dose_change : float
            Amount that will be added to each dose factor (columns first, then rows).
        selection : string
            Query string to make a selection on which to perform the operation.

        Examples
        --------
        >>> import gdstk
        >>> import voyager as vyg
        >>> lib = gdstk.Library()
        >>> ld = {"layer": 0, "datatype": 1000}
        >>> cell_1 = lib.newCell("cell1")
        >>> cell_2 = lib.newCell("cell2")
        >>> cell_1.add(gdstk.rectangle((0,0), (100,100), **ld))
        >>> cell_2.add(gdstk.ellipse((0,0), 50, **ld))
        >>> pls1 = vyg.Positionlist(WaferLayout='12x12mm.wlo')
        >>> pls1.add(cell_1, (3,3))
        >>> pls1.add(cell_2, (3.2,3))
        >>> pls1.plot()
        >>> pls1.matrixCopy(size=(2,3), row_vector=(0,4), column_vector=(3,0), dose_change=(lambda x: x+0.1), selection="Comment='cell1'")
        >>> pls1.plot()
        """
        indices = self.df.query(selection).index
        for i in range(size[0]):
            for j in range(size[1]):
                if (i,j) != (0,0):
                    for k in indices:
                        self.df = self.df.append(self.df.iloc[k], ignore_index=True)
                        self.df.at[len(self)-1,'U'] += i*row_vector[0] + j*column_vector[0]
                        self.df.at[len(self)-1,'V'] += i*row_vector[1] + j*column_vector[1]
                        self.df.at[len(self)-1,'DoseFactor'] = func_n(dose_change, i*size[1]+j, self.df.at[k,'DoseFactor'])


    def assignWorkingArea(self, workingarea, selection='@ALL_VOYAGER'):
        """
        Assign a working area to the selected entries.

        Parameters
        ----------
        workingarea : voyager.WorkingArea
            The working area to be given to the positionlist. Has to be voyager.WorkingArea containing working areas for all the cells in the positionlist.
        selection : string
            Query string to make a selection on which to apply the operation.
        """
        if not isinstance(workingarea, WorkingArea):
            raise TypeError("The workingArea has to be an instance of class voyager.WorkingArea.")
        for i in range(len(self)):
            wa = np.reshape(np.array(workingarea.df[workingarea.df['cell_name'] == self.df.loc[i,'Comment']]['left', 'bottom', 'right', 'top']), 4)
            self.df.loc[i, 'Area'] = wa

    def write(self, filename, view='default'):
        """
        Write the Positionlist object to a .pls file.

        Parameters
        ---------
        filename : string
            The name of the pls file (with .pls extension)
        view : string
            This determines which columns of the positionlist are visible in the VOYAGER. Possible options are "default" and "minimal".
        """
        if any(pd.isnull(self.df['File'])):
            raise Exception("There are entries with an unassigned file. Use voyager.Positionlist.assignFile() first.")
        if any(pd.isnull(self.df['Area'])):
            raise Exception("There are entries of cells without a definded area present. Use voyager.Positionlist.updateArea() before writing.")
        df2 = self.df.copy(deep=True)
        df2['Area'] = df2['Area'].apply(lambda x: ";".join(str(x).replace('[','').replace(']','').split()))
        df2['Layer'] = df2['Layer'].apply(lambda x: ";".join(str(x).replace('[','').replace(']','').split()))
        with open(filename, "w") as f:
            f.write(pls_header(self.df, self.wlo, view) + df2.to_csv(header=False, index=False))

    def setLayer(self, layer, selection='@ALL_VOYAGER'):
        """
        Change the layers of the selected entries.

        Parameters
        ----------
        layers : list of int or int
            The layers to which you want to change the selected entries.
        selection : string
            Query string with which you make a selection. Defaults to all.
        """
        layer = np.array(layers).flatten()
        for i in self.df.query(selection).index:
            self.df.at[i,'Layer'] = layers

    def setPosition(self, position, selection=None):
        """
        Set the position of selected entries.

        Parameters
        ----------
        position : tuple
            The position that you wish to set
        selection : string
            The query string with which you select the entries you wish to change.
        """
        self.df.loc[self.df.query(selection).index, 'U'] = position[0]
        self.df.loc[self.df.query(selection).index, 'V'] = position[1]

    def setLink(self, link, selection='@ALL_VOYAGER'):
        """Set Link for the selected entries."""
        self.df.loc[self.df.query(selection).index, 'Link'] = link

    def setDoseFactor(self, dosefactor, selection='@ALL_VOYAGER'):
        """Set dose factor for the selected entries."""
        self.df.loc[self.df.query(selection).index, 'DoseFactor'] = dosefactor

    def setArea(self, area, selection='@ALL_VOYAGER'):
        """
        Set the area of the selected entries.

        Parameters
        ----------
        area : numpy.array or list of len 4
            The area we want to set the for the entries. Syntax is [left, bottom, right, top].
        selection : string
            Query string providing the selection on which to set the areas (defaults to ALL).
        """
        area = np.array(area).flatten()
        if len(area) != 4:
            raise ValueError("The area has to be a numpy array or list of length 4.")
        for i in self.df.query(selection).index:
            self.df.at[i, 'Area'] = area

    def updateArea(self, overwrite=False):
        """This function updates all empty areas to the bounding box of the cells. If overwrite is passed, all areas will be updated to the bounding boxes instead."""
        if overwrite:
            for i in range(len(self)):
                self.df.at[i,'Area'] = rounderupper(np.array(self.cells[self.df.at[i,'Comment']].bounding_box()).flatten())
        else:
            for i in np.where(pd.isnull(self.df['Area'])==True)[0]: 
                self.df.at[i,'Area'] = rounderupper(np.array(self.cells[self.df.at[i,'Comment']].bounding_box()).flatten())


    def toggleStepsize(self):
        """Toggle the usage of stepsize (necessary for dual beam)."""
        if 'StepsizeU' not in self.df:
            self.df['StepsizeU'] = ['' for x in range(len(self))]
            self.df['StepsizeV'] = ['' for x in range(len(self))]
            self.df['CurveLine'] = ['' for x in range(len(self))]
        else:
            self.df = self.df.drop(['StepsizeU', 'StepsizeV', 'CurveLine'], axis=1)

    def setStepsize(self, stepsize, selection='@ALL_VOYAGER'):
        """
        Set StepsizeU and StepsizeV for the selected entries

        Parameters
        ----------
        stepsize : float or tuple
            The U and V stepsize. If not tuple, stepsizeU and stepsizeV will be the same.
        selection : string
            Query string with which to select the entries.
        """
        if isinstance(stepsize, float) or isinstance(stepsize, int):
            stepsize = (stepsize, stepsize)
        self.df.loc[self.df.query(selection).index, 'StepsizeU'] = stepsize[0]
        self.df.loc[self.df.query(selection).index, 'StepsizeV'] = stepsize[1]

    def setWaferlayout(self, wlo):
        """Set the wafer layout of the positionlist"""
        self.wlo = wlo

    def plot(self, writefield=200, flatten=False, order=False):
        """
        Plot the position of the cells in the current positionlist on the currently selected wafer.
        
        Parameters
        ----------
        writefield : float
            The size of the writefield you intend to use
        flatten : bool
            If flatten is passed, the plot will show the polygons where they will end up.
        order : bool
            If order is passed, the order in which structures will be written is visible.
        """
        fig, ax = plt.subplots(figsize=(10,10))
        ax.set_facecolor('gray')
        ax.set_aspect(aspect=1)
        ax.set_xlim(np.array(wafermaps[self.wlo].get_extents())[:,0])
        ax.set_ylim(np.array(wafermaps[self.wlo].get_extents())[:,1])
        ax.add_patch(copy(wafermaps[self.wlo]))
        if flatten:
            if order:
                number = 0
            layer = np.unique(np.concatenate(self.df['Layer']))
            for i in range(len(self)):
                area = self.df.at[i,'Area']
                pos = (1e3*self.df.loc[i,'U']-writefield/2-area[0], 1e3*self.df.loc[i,'V']-writefield/2-area[1])
                for j in self.cells[self.df.loc[i,'Comment']].polygons:
                    poly = j.copy()
                    ax.add_patch(Polygon(poly.translate(pos).points, closed=True, fc=colours[j.layer]))
                    if order:
                        bounds = np.array(poly.bounding_box()).flatten()
                        plt.text((bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2, str(number), horizontalalignment='center', verticalalignment='center')
                        number += 1
        else:
            for i in range(len(self)):
                pos = (1e3*self.df.loc[i,'U']-writefield/2, 1e3*self.df.loc[i,'V']-writefield/2)
                area = self.df.at[i,'Area']
                ax.add_patch(Rectangle(pos, area[2]-area[0], area[3]-area[1], fc='black'))
                plt.text(1e3*self.df.loc[i,'U']+(area[2]-area[0]-writefield)/2, 1e3*self.df.loc[i,'V']+(area[3]-area[1]-writefield)/2, self.df.loc[i,'Comment'], horizontalalignment='center', verticalalignment='center', color='gray')
            if order:
                ax.plot(self.df['U'], self.df['V'], color='red')

        plt.show()
        
    def shortSortCells(self):
        """Sort the polygons in the cells such that the ones closest to each other are written after each other."""
        for i in self.cells:
            polygons = self.cells[i].polygons()
            self.cells[i].remove(*polygons)
            polygons.sort(key=polygon_key)
            self.cells[i].add(*polygons)


def read_pls(filename):
    """
    Reads the selected file into a Positionlist.
    
    Parameters
    ----------
    filename : string
        The path to the file to be read

    Returns
    -------
    out : voyager.Positionlist
        Positionlist containing the data in the file.
    """
    with open(filename, "r") as f:
        content = f.read().splitlines()
    index_HEADER = content.index('[HEADER]')
    index_COLUMNS = content.index('[COLUMNS]')
    index_DATA = content.index('[DATA]')
    index_WAFERLAYOUT = [i.find('WAFERLAYOUT') for i in content].find(0)
    wlo = content[index_WAFERLAYOUT][content[index_WAFERLAYOUT].find('=')+1:]
    poslist = Positionlist(WaferLayout=wlo)
    columns = []
    for i in content[index_COLUMNS:index_DATA]:
        if i.find != -1:
            name = i[0:i.find('=')]
            if name != 'No.':
                columns.append(name)
    poslist.df = pd.read_csv(filename, header=index_DATA, names=columns, skip_blank_lines=False)
    return poslist
        

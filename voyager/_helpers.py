import random
import numpy as np
from matplotlib.patches import Rectangle, Ellipse

random.seed(12)
colours = [(random.random(), random.random(), random.random()) for x in range(100)]
random.seed()

wafermaps = {'3 inch left.wlo': Ellipse((0,0),1e3*76.2,1e3*76.2,facecolor='w'), '4 inch left.wlo': Ellipse((0,0),1e5,1e5,facecolor='w'), '4.8x4.8.wlo': Rectangle((0,0),1e3*4.8,1e3*4.8,facecolor='w'), '10x10.wlo': Rectangle((0,0),1e4,1e4,facecolor='w'), '12x12mm.wlo': Rectangle((0,0),1e3*12,1e3*12,facecolor='w'), '20mm2.wlo': Rectangle((0,0),1e3*20,1e3*20,facecolor='w'), '24mm2.wlo': Rectangle((0,0),1e3*24,1e3*24,facecolor='w'), '50x50.wlo': Rectangle((0,0),1e3*50,1e3*50,facecolor='w'), 'Bare_4inch.wlo': Ellipse((0,0),1e5,1e5,facecolor='w'), 'Bare_6inch.wlo': Ellipse((0,0),15e4,15e4,facecolor='w'), 'Bare_8inch.wlo': Ellipse((0,0),2e5,2e5,facecolor='w'), 'DEFAULT.wlo': Ellipse((0,0),15e4,15e4,facecolor='w')}

ALL_VOYAGER = slice(None) # defined for pandas.DataFrame.query()

visible_default = {'ID':25, 'U':50, 'V':50, 'Attribute':55, 'Template':55, 'Comment':100, 'Options':165, 'Type':85, 'Pos1':85, 'Pos2':85, 'Pos3':85, 'Link':25, 'File':154, 'Layer':80, 'DoseFactor':55, 'FBMSArea':88, 'FBMSLines':81, 'Time':85, 'Time':85, 'StepsizeU':50, 'StepsizeV':50, 'CurveLine':50} 
showdim_default = {'X':None, 'Y':None, 'Z':None, 'R':None, 'T':None, 'U':None, 'V':None, 'W':None, 'Size-U':'um', 'Size-V':'um', 'Points-U':'px', 'Points-V':'px', 'Pos1':'um', 'Pos2':'um', 'Pos3':'um', 'Dwelltime':'ms', 'Stepsize':'um', 'SplDwell':'ms', 'SplStep':'um', 'CurveStep':'um', 'CurveDwell':'ms', 'DotDwell':'ms', 'FBMSArea':'mm/s', 'FBMSLines':'mm/s'}
default_values_default = {'Attribute':'A', 'Template':'UV'}
visible_minimal = {'ID':25, 'U':50, 'V':50, 'Comment':100, 'File':154, 'Layer':80, 'DoseFactor':55, 'StepsizeU':50, 'StepsizeV':50}
showdim_minimal = {'U':'mm', 'V':'mm', 'StepsizeU':'um', 'StepsizeV':'um'}
default_values_minimal = {'Attribute':'A', 'Template':'UV'}

def func_n(func, n, x):
    for i in range(n):
        x = func(x)
    return x

def pls_header(df, waferlayout, view):
    if view == 'default':
        visible = visible_default
        default = default_values_default
        showdim = showdim_default
    elif view == 'minimal':
        visible = visible_minimal
        default = default_values_minimal
        showdim = showdim_minimal
    else:
        raise ValueException("Incorrect setting for view. Has to be either 'default' or 'minimal'.")
    header_exceptions=['ID','X', 'Y', 'Z', 'R', 'T', 'U', 'V', 'W', 'Attribute', 'Template', 'Comment']
    string = '\n[HEADER]\nFORMAT=IXYZRTUVWATC'
    for i in df:
        if not i in header_exceptions:
            string += ','+i+',0'
    string += '\nWAFERLAYOUT=' + waferlayout + '\nLotID=\nWaferID=\nSlot=\nMinimizeWin=FALSE\n\n[COLUMNS]\nNo.=W:25,!VISIBLE,!SHOWDIM\n'
    for i in df:
        string += i + '='
        if i in visible.keys():
            string += 'W:{},VISIBLE'.format(visible[i])
        else:
            string += 'W:50,!VISIBLE'
        if i in default.keys():
            string += ',DEFAULT:{}'.format(default[i])
        if i in showdim.keys():
            if showdim[i] != None:
                string += ',DIM:{},SHOWDIM\n'.format(showdim[i])
            else:
                string += ',SHOWDIM\n'
        else:
            string += ',!SHOWDIM\n'
    string += '\n[DATA]\n'
    return string

def rounderupper(x,n=2):
    """ Function to return an array 'x', rounded up to a precision 'n'."""
    return np.sign(x)*np.ceil(10**n*np.abs(x))/10**n

def dist(matrix, path):
    return sum([matrix[path[i],path[i+1]] for i in range(len(path)-1)])

def distMatrix(arr):
    matrix = np.zeros((len(arr),len(arr)), dtype=float) 
    for i in range(len(arr)):
        for j in range(len(arr)):
            matrix[i,j] = abs(arr[i,0]-arr[j,0]) + abs(arr[i,1]-arr[j,1])
    return matrix

def entry_adder(df, cell, position, layer, dosefactor):
    if cell.bounding_box() is None:
        bounds = np.nan
        SizeU, SizeV = np.nan, np.nan
    else:
        bounds = np.array(cell.bounding_box()).flatten()
        SizeU, SizeV = abs(bounds[2]-bounds[0]), abs(bounds[3]-bounds[1])

    dictionary = dict()
    for i in df:
        dictionary[i] = np.nan
    dictionary['Comment'], dictionary['U'], dictionary['V'], dictionary['Layer'], dictionary['DoseFactor'] = cell.name, position[0], position[1], layer, dosefactor
    dictionary['ID'] = len(df)
    dictionary['Area'] = rounderupper(bounds)
    dictionary['Pos1'], dictionary['Pos2'] = SizeU/2, SizeV/2
    dictionary['Attribute'] = 'XN'
    dictionary['Template'] = 'UV'
    dictionary['Type'] = 'EXPOSURE'
    return dictionary

def polygon_key(polygon):
    """ Sort polygons by bounding box"""
    bb = polygon.bounding_box()
    return bb[0]

import numpy as np
import xarray as xr

__all__ = ["get_maskedcube", "chopper_wheel", "make_grid", "baseline_fitting"]

def get_maskedcube(cube, obsmode, scan_number):#片方maskにも対応させる
    obsmask = cube["obsmode"] == obsmode
    scanmask = cube["scannum"] == scan_number
    mask = np.logical_and(obsmask, scanmask)
    return cube[mask]
    
def chopper_wheel(on, off, hot, Tamb):
    return Tamb * (on - off)/(hot - off)


def make_grid(lamda_on, beta_on, N, grid):
    azgrid = np.arange(lamda_on + ((N-1)/2)*grid, lamda_on - ((N-1)/2+1)*grid, grid*-1)
    elgrid = np.arange(beta_on - ((N-1)/2)*grid, beta_on + ((N-1)/2+1)*grid, grid)
    azel_grid = np.meshgrid(azgrid, elgrid)
    return azel_grid

def fitting_func3(x, a, b, c, d):
     return a*x**3 + b*x**2 + c*x**1 + d

def fitting_func2(x, a, b, c):
     return a*x**2 + b*x**1 + c

def fitting_func1(x, a, b):
     return a*x + b

def baseline_fitting(arr_x, arr_y, index1, index2, index3, index4, order=1):
    tmpdata_y1 = arr_y[index1:index2]
    tmpdata_y2 = arr_y[index3:index4]
    tmpdata_x1 = arr_x[index1:index2]
    tmpdata_x2 = arr_x[index3:index4]
    x = np.concatenate([tmpdata_x1, tmpdata_x2])
    y = np.concatenate([tmpdata_y1, tmpdata_y2])
    param = np.polyfit(x, y, order)
    if order == 1:
        arr_y = arr_y - fitting_func1(arr_x, *param)
    elif order == 2:
        arr_y = arr_y - fitting_func2(arr_x, *param)
    elif order == 3:
        arr_y = arr_y - fitting_func3(arr_x, *param)
    else:
        pass
    return arr_y


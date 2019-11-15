import numpy as np
import xarray as xr

__all__ = ["get_maskedcube", "chopper_wheel", "make_grid"]

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

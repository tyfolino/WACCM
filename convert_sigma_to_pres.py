# This script takes input in the form of a netCDF file on hybrid sigma coordinates and converts it to standard
# pressure levels

# By: Tyler Paul Folino Janoski
# Updated: 01.15.20

# Import statements

import xarray as xr
import ngl
import numpy as np

# Let's create a function to easily read in data

def read_in(case,exp,mon,ens,var):
    """
    Use xarray to read in a netCDF file.
    
    Keyword arguments:
    case -- output case prefix (b40.1850, f1850)
    exp -- CO2 scenario
    mon -- starting month in which CO2 is altered
    ens -- ensemble number
    var -- model output variable
    """
    filein = '/dx05/tylerj/d10/Arctic_Research/WACCM/output/'+case+'.scwc.'+exp+'.01.0'+str(
        f"{mon:02d}")+'.0'+str(f"{ens:02d}")+'.h1_'+var+'.nc'
    return(xr.open_dataset(filein,chunks=None))

# iterate through all files
#for a in ['b40.1850','f1850']:
#    for b in ['4xCO2','ctrl']:
for a in ['b40.1850']:
    for b in ['4xCO2']:
        for c in range(12):
            for d in range(10):
                for e in ['T','Q','U','V']:
                    print(a,b,c,d,e)
                    # read in dataset
                    ds = read_in(a,b,c+1,d+1,e)

                    # create list of pressure levels (corresponding to pressure levels of kernels)
                    plevs = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10,
                            7, 5, 3, 2, 1, 0.5, 0.2, 0.1]

                    # Use ngl to perform linear vertical interpolation to those pressure levels 
                    # without extrapolation
                    ds_new = ngl.vinth2p(ds[e],ds.hyam,ds.hybm,plevs,ds.PS,1,ds.P0/100,1,kxtrp=False)
                    ds_new[ds_new==1e30] = np.NaN

                    # make a new dataset while preserving netCDF attributes
                    ds_out = xr.Dataset({e: (('time','plev','lat','lon'), ds_new[:,:,:,:])},
                                    {'lon': ds.lon, 'lat':ds.lat, 'time':ds.time,'plev':(np.array(
                                        plevs,dtype=np.double)*100)})
                    ds_out.attrs = ds.attrs
                    ds_out[e].attrs = ds[e].attrs
                    ds_out.plev.attrs['units'] = 'Pa'
                    ds_out.plev.attrs['long_name'] = 'pressure level'
                    
                    # save at netCDF file
                    fileout = '/dx02/tylerj/WACCM/vert_pres/'+a+'.scwc.'+b+'.01.0'+str(
                        f"{c+1:02d}")+'.0'+str(f"{d+1:02d}")+'.h1_'+e+'_pres.nc'
                    ds_out.to_netcdf(path=fileout)

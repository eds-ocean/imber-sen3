# %%
import os, shutil, gc, glob

import planetary_computer
import pystac_client
import fsspec

from getpass import getpass

import xarray as xr
import numpy as np
import cf_xarray, rioxarray

import time
from datetime import datetime, timedelta

from cdo import *
cdo = Cdo()
cdo.cleanTempDir()

from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib import cm
import colormaps as cmo

from cartopy import crs as ccrs
from cartopy import feature as cf

import zipfile

#from rich.jupyter import print as rprint
from rich.table import Table
from rich.markdown import Markdown
from rich.console import Console
console = Console()

import warnings
warnings.filterwarnings('ignore')

from tqdm.auto import tqdm

# %%
download_dir = os.path.join(os.getcwd(),"sentinel-3_program","downloaded-data")
result_dir = os.path.join(os.getcwd(),"sentinel-3_program","processed-data")

os.makedirs(download_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

cleardown = glob.glob(os.path.join(download_dir, "*"))

for file in cleardown:
    os.remove(file)

clearres = glob.glob(os.path.join(result_dir, "*"))
clearres = [f for f in clearres if "Sen-3" not in f]

for file in clearres:
    os.remove(file)

# %%
list_flags_common = ['LAND','INLAND_WATER','COASTLINE','CLOUD','CLOUD_AMBIGUOUS','CLOUD_MARGIN','INVALID','COSMETIC','SATURATED','SUSPECT','HISOLZEN','HIGHGLINT','SNOW_ICE']
list_flags_process = ['AC_FAIL','WHITECAPS','ADJAC','RWNEG_O2','RWNEG_O3','RWNEG_O4','RWNEG_O5','RWNEG_O6','RWNEG_O7','RWNEG_O8']
list_flags_oc4me = ['OC4ME_FAIL','TIDAL']
list_flags_ocnn = ['OCNN_FAIL']

def flag_data_fast(list_flag, flag_names, flag_values, flag_data, flag_type='WQSF'):
    flag_bits = np.uint64()
    if flag_type == 'SST':
        flag_bits = np.uint8()
    elif flag_type == 'WQSF_lsb':
        flag_bits = np.uint32()
    for flag in list_flag:
        try:
            flag_bits = flag_bits | flag_values[flag_names.index(flag)]
        except:
            print(flag + ' not present')
    return (flag_data & flag_bits) > 0			


# %%
time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

area_md = '''
### 🌏  Area of Interest
Please input coordinates of your area of interest. The coordinates should be in **decimal format** with minus (➖) sign for south-of-equator latitude or west-of-greenwich longitude.
'''
# Area of interest
console.print(Markdown(area_md))

north = float(input('North point: ')) # -6.85
south = float(input('South point: ')) # -7.95
west = float(input('West point: ')) # 112.66
east = float(input('East point: ')) # 114.65


# %%
area_of_interest = {
    "type": "Polygon",
    "coordinates": [
        [
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
        ]
    ],
}


extent = [west, east, south, north]
bbox = [west, south, east, north]

bbox_str = f'{west},{east},{south},{north}' 

def format_coordinate(value, is_latitude):
    if is_latitude:
        suffix = "S" if value < 0 else "N"
    else:
        suffix = "W" if value < 0 else "E"

    return f"{abs(value)}{suffix}"

north_str = format_coordinate(north, is_latitude=True)
south_str = format_coordinate(south, is_latitude=True)
west_str = format_coordinate(west, is_latitude=False)
east_str = format_coordinate(east, is_latitude=False)

geostr = f"{north_str}_{south_str}_{west_str}_{east_str}"

# %%
# Create a dummy dataset based on the area of interest
resolution = 300
resolution_degrees = resolution / 111320

num_lon = int(np.ceil((east - west) / resolution_degrees)) + 1
num_lat = int(np.ceil((north - south) / resolution_degrees)) + 1

lon = np.linspace(west, east, num_lon)
lat = np.linspace(south, north, num_lat)

ds = xr.Dataset(
    coords={
        "lon": (["lon"], lon),
        "lat": (["lat"], lat),
    }
)

ds.lat.attrs = {
    'units' : 'degrees_north',
    'unit_long' : "Degrees North",
    'standard_name' : "latitude",
    'long_name' : "Latitude",
    'axis' : 'Y'
}

ds.lon.attrs = {
    'units' : 'degrees_east',
    'unit_long' : "Degrees East",
    'standard_name' : "longitude",
    'long_name' : "Longitude",
    'axis' : 'X'
}

ds["data"] = (["lat", "lon"], np.zeros((num_lat, num_lon)))

ds.rio.write_crs('epsg:4326', inplace=True)

ds.to_netcdf(download_dir + '/grid_data.nc')

dsinput = download_dir + '/grid_data.nc'
grids = cdo.griddes(input = dsinput)
gridfile = os.path.join(os.getcwd(), 'gridfile.txt') 

with open(gridfile, 'w') as f:
    print("\n".join(line.strip("'") for line in grids), file = f)

ds.close()
gc.collect()

# %%
time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

## Time of interest
time_md = '''
### 🕒  Time of Interest

Please input the start and end of your time of interest. The dates should be in `YYYY-MM-DD` format. This program will select data available between the the times, and returned dataset time might be different due to the availability.
'''

console.print(Markdown(time_md))

print()
dtstart = input('Time start: ')
dtend = input('Time end: ')

time_of_interest = f"{dtstart}/{dtend}"

# %%
time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

params_md = '''
### 📊  Dataset Parameter

Please select dataset parameters you want to download. 

1. Download geophysical parameters (chlorophyll-a and total suspended matter)
2. Download water surface reflectances.
'''

console.print(Markdown(params_md))

print()

while True:
    parameters = int(input('Parameters: '))

    if parameters == 1:
        nick = 'geophysical-data'
        print()
        print('Geophysical parameters will be processed.')
        break
    elif parameters == 2:
        nick = 'optical-data'
        print()
        print('Water surface reflectances will be processed.')
        break
    else:
        print("You put wrong number. Please try again!")

# %%
catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
search = catalog.search(collections=["sentinel-3-olci-wfr-l2-netcdf"], intersects=area_of_interest, datetime=time_of_interest)

items = search.item_collection()

# %%
table = Table(title = "Summary")

table.add_column("Released", justify="left", style="cyan", no_wrap=True)
table.add_column("Title", justify="left", style="magenta")

table.add_row(f"Area of interest",f"{geostr}")
table.add_row(f"Time of interest",f"{time_of_interest}")
table.add_row(f"Number of items",f"{len(items)}")
table.add_row(f"First dataset",f"{items[-1].properties['datetime']}")
table.add_row(f"last dataset",f"{items[0].properties['datetime']}")

console.print(table)

# %%
print()

for i in range(3, 0, -1):
    print(f"Process will be started in ... {i} ", end="\r", flush=True)
    time.sleep(1) 

os.system('cls' if os.name == 'nt' else 'clear') 

for index, item in tqdm(enumerate(items, start=1), desc="Processing: ", total = len(items), position=0, leave=False):
    try:
        console.log(f'Processing data #{index} started.')
        file_id = item.id
    
        date_string = item.properties['datetime']
        timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        
        console.log(f'Dataset #{index}: Reading.')
        coord_file = xr.open_dataset(fsspec.open(item.assets["geo-coordinates"].href).open())
        flags_file = xr.open_dataset(fsspec.open(item.assets["wqsf"].href).open())
        
        flag_names = flags_file['WQSF'].flag_meanings.split(' ')
        flag_vals = flags_file['WQSF'].flag_masks
        flags_data = flags_file.variables['WQSF'].data
    
        dta = xr.Dataset()
        dta['longitude'] = coord_file['longitude']
        dta['latitude'] = coord_file['latitude']
        
        coord_file.close()
        flags_file.close()
        gc.collect()
    
        console.log(f'Dataset #{index}: Applying flags.')
    
        if parameters == 1:
            keys = ["chl-nn","tsm-nn","chl-oc4me"]
            for k in keys:
                if not k == 'chl_oc4me':
                    list_flags = list_flags_common + list_flags_ocnn
                else:
                    list_flags = list_flags_common + list_flags_process + list_flags_oc4me
        
                ds = xr.open_dataset(fsspec.open(item.assets[k].href).open())
                da = ds[[var for var in ds.variables if "_err" not in var][0]]
                ds.close()
        
                dtarr = da.data
        
                flag_mask = flag_data_fast(list_flags, flag_names, flag_vals, flags_data, flag_type='WQSF')
                
                flagged = np.where(flag_mask, np.nan, dtarr)
                
                dta[str(k)] = xr.DataArray(flagged, dims=('rows','columns'))
                dta[str(k)].attrs = da.attrs
        
                del ds
                del da
                del dtarr
        
        elif parameters == 2:
            keys = ['Oa01-reflectance','Oa02-reflectance','Oa03-reflectance','Oa04-reflectance','Oa05-reflectance','Oa06-reflectance','Oa07-reflectance','Oa08-reflectance','Oa09-reflectance','Oa10-reflectance','Oa11-reflectance','Oa12-reflectance','Oa16-reflectance','Oa17-reflectance','Oa18-reflectance','Oa21-reflectance']
            list_flags = list_flags_common + list_flags_process
            for k in keys:
                ds = xr.open_dataset(fsspec.open(item.assets[k].href).open())
                da = ds[[var for var in ds.variables if "_err" not in var][0]]
                ds.close()
        
                dtarr = da.data
        
                flag_mask = flag_data_fast(list_flags, flag_names, flag_vals, flags_data, flag_type='WQSF')
                
                flagged = np.where(flag_mask, np.nan, dtarr)
                
                dta[str(k)] = xr.DataArray(flagged, dims=('rows','columns'))
                dta[str(k)].attrs = da.attrs
        
                del ds
                del da
                del dtarr
        
        dta = dta.set_coords(['latitude','longitude'])
        dta = dta.expand_dims(dim={"time":[timestamp]}, axis=0)
    
        console.log(f'Dataset #{index}: Subsetting.')
    
        reggrid = cdo.sellonlatbox(bbox_str, input = dta, returnXDataset = True)
        
        comp = dict(zlib=True, _FillValue=-99999.0, complevel=4)
        encoding = {var: comp for var in reggrid.data_vars}
        
        reggrid.to_netcdf(
            os.path.join(download_dir , file_id + f'_{nick}.nc'),
            format='NETCDF4', 
            unlimited_dims=['time'],
            encoding=encoding
        )
        
        dta.close()
        del reggrid
        cdo.cleanTempDir()
        gc.collect()
    
        console.log(f'Dataset #{index}: Regridding.')
    
        dataset = xr.open_dataset(os.path.join(download_dir , file_id + f'_{nick}.nc'), decode_coords="all")
        dataset = dataset.cf.add_bounds(['latitude','longitude'])
        
        reggridded = cdo.remapcon(gridfile, input = dataset, returnXDataset = True)
        
        comp = dict(zlib=True, _FillValue=-99999.0, complevel=4)
        encoding = {var: comp for var in reggridded.data_vars}
        
        reggridded.to_netcdf(
            os.path.join(result_dir , file_id + f'_{nick}.nc'),
            format='NETCDF4', 
            unlimited_dims=['time'],
            encoding=encoding
        )
    
        dataset.close()
        del reggridded
        cdo.cleanTempDir()
        gc.collect()
    
        console.log(f'Dataset #{index}: Finished')
    
        time.sleep(0.5)
        os.system('cls' if os.name == 'nt' else 'clear') 
    except:
        continue

# %%
console.log(f'Combining dataset.')

files = glob.glob(os.path.join(result_dir , f'S3*{nick}.nc'))
ds = xr.open_mfdataset(files)

ds_day = ds.resample(time="D").mean()

ds.close()
gc.collect()

console.log(f'Saving result.')

ds_day.to_netcdf(
    os.path.join(result_dir, f'Sen-3_{str(ds.time[0].data)[0:10]}_{str(ds.time[-1].data)[0:10]}_{geostr}_{nick}.nc'),
    format = 'NETCDF4', 
    encoding = {var: comp for var in ds_day.data_vars}
)

console.log(f'All process done! 😎')

time.sleep(3)

md_end = f"""
Processing requested dataset succesfull. You can now download your data by accessing this path `{os.path.join(result_dir, f'Sen-3_{str(ds.time[0].data)[0:10]}_{str(ds.time[-1].data)[0:10]}_{geostr}_{nick}.nc')}` from the sidebar.
"""

console.print(Markdown(md_end))

time.sleep(5)

# %%
files_to_delete = glob.glob(os.path.join(result_dir, "*.nc"))
files_to_delete = [f for f in files_to_delete if "Sen-3" not in f]

for file in files_to_delete:
    os.remove(file)

#display(ds)

# %%




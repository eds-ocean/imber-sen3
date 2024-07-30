#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os, shutil, gc, glob

import hda
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

from rich.jupyter import print as rprint
from rich.table import Table
from rich.markdown import Markdown
from rich.console import Console
console = Console()


import warnings
warnings.filterwarnings('ignore')

from tqdm.auto import tqdm


# In[ ]:


download_dir = os.path.join(os.path.expanduser('~'),"sentinel-3_program","downloaded-data")
result_dir = os.path.join(os.path.expanduser('~'),"sentinel-3_program","processed-data")

os.makedirs(download_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

cleardown = glob.glob(os.path.join(download_dir, "*"))

for file in cleardown:
    os.remove(file)

clearres = glob.glob(os.path.join(result_dir, "*"))
clearres = [f for f in clearres if "Sen-3" not in f]

for file in clearres:
    os.remove(file)


# In[ ]:


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
            print(flag + 'not present')
    return (flag_data & flag_bits) > 0			


# In[ ]:


os.system('cls' if os.name == 'nt' else 'clear') 

intro_md = '''
# Welcome to Sentinel-3 OLCI Biogeochemical Data Access Program

This program is developed by Edwards Taufiqurrahman and the Integrated Marine Biosphere Research Group, Research Centre for Oceanography, National Research and Innovation Agency, Indonesia.

At first, you will be asked the WEkEO `Username` and `Password` and data that you need. Therefore, before start, please make sure that you have a WEkEO Account (you can create one from this link: [https://www.wekeo.eu/register](https://www.wekeo.eu/register)) and you should already know some information about data that you need.

### Enter your WEkEO Credential
'''

rprint(Markdown(intro_md))

print()

while True:
    try:
        user = input("Enter your WEkEO username: ")
        passw = getpass("Enter your WEkEO password: ")
        c = hda.Client(hda.Configuration(user=user, password=passw), progress=True, max_workers=1)
        print()
        print(f"Login successfull!. Your token is {c.token}.")
        break
    except KeyError:
        print()
        print('You entered wrong username and/or password.')


# In[ ]:


time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

sat_md_1 = '''
### Enter Satellite Parameters

Sentinel-3 program have 2 satellites: Sentinel-3A (launched 16 February 2016) and Sentinel-3B (launched 25 April 2018).

However, the Sentinel-3 Level 2 dataset in WEkEO are available in two type:

1. `EO:EUM:DAT:SENTINEL-3:0556` &rarr; Reprocessed dataset (25 April 2016 - 28 April 2021)
2. `EO:EUM:DAT:SENTINEL-3:OL_2_WFR___` &rarr; (5 July 2017 - recent)

#### Enter the satellite designation (`A` or `B`):

- `A` = Sentinel-3A
- `B` = Sentinel-3B

Leave it blank if you want both Sentinel-3A and Sentinel-3B queried.

'''

rprint(Markdown(sat_md_1))
print()

sat_nm = input("Satellite name: ")

print()

if sat_nm == 'a' or sat_nm == 'A':
    sat = 'Sentinel-3A'
    print()
elif sat_nm == 'b' or sat_nm == 'B':
    sat = 'Sentinel-3B'
    print()
else:
    sat = ''
    print()

sat_md_2 = '''

#### Enter Sentinel-3 dataset ID (`1` or `2`)

1. EO:EUM:DAT:SENTINEL-3:0556
2. EO:EUM:DAT:SENTINEL-3:OL_2_WFR___
'''

rprint(Markdown(sat_md_2))

print()

while True:
    sat_id = int(input('Satellite ID: '))

    if sat_id == 1:
        dataset_id = 'EO:EUM:DAT:SENTINEL-3:0556'
        print()
        break
    elif sat_id == 2:
        dataset_id = 'EO:EUM:DAT:SENTINEL-3:OL_2_WFR___'
        print()
        break
    else:
        print()
        rprint("You put wrong number. Please try again!")

print()


# In[ ]:


time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

area_md = '''
Please input your area of interest. The coordinates should be in **decimal format** with minus (`-`) sign for south-of-equator latitude or west-of-greenwich longitude.
'''
# Area of interest
rprint(Markdown(area_md))

north = float(input('North point: ')) # -6.85
south = float(input('South point: ')) # -7.95
west = float(input('West point: ')) # 112.66
east = float(input('East point: ')) # 114.65

bbox = [west, south, east, north]
extent = [west, east, north, south]
bbox_str = f'{west},{east},{south},{north}' 

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


# In[ ]:


time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

## Time of interest
time_md = '''
### Time of Interest

Please input the start date and end date of your interest. The dates should be in `YYYY-MM-DD` format. Only use the time period suitable for your selected dataset.
'''

rprint(Markdown(time_md))

print()
dtstart = input('Time start: ')
dtend = input('Time end: ')


# In[ ]:


time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

params_md = '''
Please select what parameters you want to download. 

1. Download geophysical (chlorophyll-a and total suspended matter)
2. Download water surface reflectances.
'''
rprint(Markdown(params_md))

print()

while True:
    parameters = int(input('Parameters: '))

    if parameters == 1:
        nick = 'geophysical-data'
        print()
        print('Geophysical data will be processed.')
        break
    elif parameters == 2:
        nick = 'optical-data'
        print()
        print('Reflectance data will be processed.')
        break
    else:
        print("You put wrong number. Please try again!")


# In[ ]:


time.sleep(1)
os.system('cls' if os.name == 'nt' else 'clear') 

resume_md = '''
### Data Query

Below is the resume of data query based on your input.
'''

query = {
  "dataset_id": dataset_id, 
  "dtstart": dtstart,
  "dtend": dtend,
  "bbox": bbox,
  "sat": sat,
  "type": "OL_2_WFR___",
  "timeliness": "NT"
}

query_tab = Table(title="Search Query")
query_tab.add_column('Parameter', style='cyan')
query_tab.add_column('Value', style='bright_green')

for col1, col2 in query.items():
    query_tab.add_row(str(col1), str(col2))


rprint(Markdown(resume_md))
rprint(query_tab)

time.sleep(0.5)

search_result = c.search(query)
print(search_result)


# In[ ]:


time.sleep(3)
os.system('cls' if os.name == 'nt' else 'clear') 

for index, result in tqdm(enumerate(search_result.results, start=0), desc="Processing: ", total = len(search_result.results), position=0, leave=False):
    console.log(f'Processing data no. {index + 1} started.')
    file_id = result['id']

    start = datetime.strptime(result['properties']['startdate'], '%Y-%m-%dT%H:%M:%S%fZ')
    end = datetime.strptime(result['properties']['enddate'], '%Y-%m-%dT%H:%M:%S%fZ')
    timestamp = start + (end - start) / 2

    console.log(f'Downloading data.')
    search_result[index].download()


    with zipfile.ZipFile(file_id + '.zip', 'r') as zip_ref:
        console.log(f'Extracting data.')
        zip_ref.extractall(download_dir)
        os.remove(file_id + '.zip')

    console.log(f'Applying mask to data.')
    
    geo_coords = xr.open_dataset(os.path.join(download_dir, file_id, 'geo_coordinates.nc'))
    
    flag_file = xr.open_dataset(os.path.join(download_dir, file_id, 'wqsf.nc'))
    flag_names = flag_file['WQSF'].flag_meanings.split(' ') #flag names
    flag_vals = flag_file['WQSF'].flag_masks #flag bit values
    flags_data = flag_file.variables['WQSF'].data
        
    dta = xr.Dataset()
    dta['longitude'] = geo_coords['longitude']
    dta['latitude'] = geo_coords['latitude']
    
    geo_coords.close()
    flag_file.close()
    gc.collect()

    if parameters == 1:
        keys = ["chl_nn","tsm_nn","chl_oc4me"]
        for k in keys:
            if not k == 'chl_oc4me':
                list_flags = list_flags_common + list_flags_ocnn
            else:
                list_flags = list_flags_common + list_flags_process + list_flags_oc4me
    
            ds = xr.open_dataset(os.path.join(download_dir, file_id, f'{k}.nc'))
            dtarr = ds[str(k.upper())].data
            flag_mask = flag_data_fast(list_flags, flag_names, flag_vals, flags_data, flag_type='WQSF')
            
            flagged = np.where(flag_mask, np.nan, dtarr)
            
            dta[str(k)] = xr.DataArray(flagged, dims=('rows','columns'))
            dta[str(k)].attrs = ds[str(k.upper())].attrs
    elif parameters == 2:
        keys = ['Oa01_reflectance','Oa02_reflectance','Oa03_reflectance','Oa04_reflectance','Oa05_reflectance','Oa06_reflectance','Oa07_reflectance','Oa08_reflectance','Oa09_reflectance','Oa10_reflectance','Oa11_reflectance','Oa12_reflectance','Oa16_reflectance','Oa17_reflectance','Oa18_reflectance','Oa21_reflectance']
        list_flags = list_flags_common + list_flags_process
        for k in keys:
            ds = xr.open_dataset(os.path.join(download_dir, file_id, f'{k}.nc'))
            dtarr = ds[str(k)].data
            flag_mask = flag_data_fast(list_flags, flag_names, flag_vals, flags_data, flag_type='WQSF')
            
            flagged = np.where(flag_mask, np.nan, dtarr)
            
            dta[str(k)] = xr.DataArray(flagged, dims=('rows','columns'))
            dta[str(k)].attrs = ds[str(k)].attrs
    
    dta = dta.set_coords(['latitude','longitude'])
    dta = dta.expand_dims(dim={"time":[timestamp]}, axis=0)
    dta = dta.cf.add_bounds(['latitude','longitude'])

    console.log(f'Subsetting data.')

    reggrid = cdo.sellonlatbox(bbox_str, input = dta, returnXDataset = True)
    
    comp = dict(zlib=True, _FillValue=-99999.0, complevel=4)
    encoding = {var: comp for var in reggrid.data_vars}
    
    reggrid.to_netcdf(
        os.path.join(download_dir , file_id + f'_{nick}.nc'),
        format='NETCDF4', 
        unlimited_dims=['time'],
        encoding=encoding
    )
    
    cdo.cleanTempDir()

    dataset = xr.open_dataset(os.path.join(download_dir , file_id + f'_{nick}.nc'), decode_coords="all")

    reggridded = cdo.remapcon(gridfile, input = dataset, returnXDataset = True)
    
    comp = dict(zlib=True, _FillValue=-99999.0, complevel=4)
    encoding = {var: comp for var in reggridded.data_vars}
    
    reggridded.to_netcdf(
        os.path.join(result_dir , file_id + f'_{nick}.nc'),
        format='NETCDF4', 
        unlimited_dims=['time'],
        encoding=encoding
    )
    
    cdo.cleanTempDir()
    
    gc.collect()
    
    for allitem in os.listdir(download_dir):
        path = os.path.join(download_dir,allitem)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    console.log(f'#{index + 1} data processing done.')

    del dta
    del dataset
    del reggridded

    time.sleep(0.8)
    os.system('cls' if os.name == 'nt' else 'clear') 

#rprint("Processing done! :sunglasses: Will continue with creating timeseries dataset.")


# In[ ]:


files = glob.glob(os.path.join(result_dir , f'*{nick}.nc'))
ds = xr.open_mfdataset(files, decode_coords="all")

ds_day = ds.resample(time="D").mean()

ds_day.to_netcdf(
    os.path.join(result_dir, f'Sen-3_{str(ds.time[0].data)[0:10]}_{str(ds.time[-1].data)[0:10]}_{nick}.nc'),
    format = 'NETCDF4', 
    encoding = {var: comp for var in ds_day.data_vars}
)


# In[ ]:


time_span = (ds_day.time[-1] - ds_day.time[0]).values / np.timedelta64(1,'D') 

if time_span >= 365:
    ds_month = ds.resample(time="MS").mean()
    ds_month.to_netcdf(
        os.path.join(result_dir, f'Sen-3_{str(ds.time[0].data)[0:10]}_{str(ds.time[-1].data)[0:10]}_{nick}_monthly.nc'),
        encoding = {var: comp for var in ds_month.data_vars}
    )
    print(ds_month)
    if time_span >= 730:
        ds_season = ds.resample(time="QS-DEC").mean()
        ds_season.to_netcdf(
            os.path.join(result_dir, f'Sen-3_{str(ds.time[0].data)[0:10]}_{str(ds.time[-1].data)[0:10]}_{nick}_seasonal.nc'),
            encoding = {var: comp for var in ds_season.data_vars}
        )
        print(ds_season)


# In[ ]:


files_to_delete = glob.glob(os.path.join(result_dir, "*.nc"))
files_to_delete = [f for f in files_to_delete if "Sen-3" not in f]

for file in files_to_delete:
    os.remove(file)

#display(ds)


# In[ ]:





# In[ ]:





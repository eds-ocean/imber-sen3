#!/usr/bin/env python
# coding: utf-8

# ## Modul
# 
# Modul yang digunakan dalam script ini dapat dilihat pada cell berikut. Jika terdapat pesan error bahwa modul tidak tersedia, dapat dilakukan instalasi terlebih dahulu dengan menggunakan `conda`
# 
# ```{python}
# !conda install <module name>
# ```
# 
# Atau bisa menggunakan `pip`
# 
# ```{python}
# !pip install <module name>
# ```
# 
# Instalasi menggunakan `pip` hendaknya dilakukan jika modul tidak tersedia dalam repository `conda`.

# In[ ]:


import os, shutil, gc

import hda
from webdav3.client import Client
from getpass import getpass

import xarray as xr
import numpy as np
import cf_xarray

from datetime import datetime

from cdo import *
cdo = Cdo()
cdo.cleanTempDir()

from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib import cm
import colormaps as cmo

from cartopy import crs as ccrs
from cartopy import feature as cf
from shapely import geometry
from shapely.geometry import shape

import zipfile

from rich.jupyter import print
from rich.markdown import Markdown

import warnings
warnings.filterwarnings('ignore')

#import gc
#import sys
#from tqdm.auto import tqdm
#import json
#import time
#import base64
#import requests
#from IPython.core.display import HTML
#import cartopy


# In[ ]:


download_dir = os.path.join(os.path.expanduser('~'),"edskywalker", "downloaded-data")
result_dir = os.path.join(os.path.expanduser('~'),"edskywalker","processed-data")

os.makedirs(download_dir, exist_ok=True)
os.makedirs(result_dir, exist_ok=True)

print(download_dir)


# In[ ]:


list_flag_nn = ['LAND', 'INLAND_WATER', 'COASTLINE', 'CLOUD', 'CLOUD_AMBIGUOUS', 'CLOUD_MARGIN', 'INVALID', 'COSMETIC', 'SATURATED', 'SUSPECT', 'HISOLZEN', 'HIGHGLINT', 'SNOW_ICE', 'AC_FAIL', 'WHITECAPS', 'ADJAC', 'RWNEG_O2', 'RWNEG_O3', 'RWNEG_O4', 'RWNEG_O5', 'RWNEG_O6', 'RWNEG_O7', 'RWNEG_O8', 'OCNN_FAIL']

# 'TIDAL', 

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


# ## Input `username` dan `password` 
# 
# Untuk mengakses data WEKEO, Anda perlu memiliki akun terlebih dahulu. Silakan pelajari mengenai pembuatan akun terlebih dahulu di [sini](https://help.wekeo.eu/en/articles/9389186-how-to-create-a-wekeo-account). 

# In[ ]:


print("Please enter your [bold u cyan]username[/bold u cyan] and [bold u cyan]password[/bold u cyan]")

user = input("Enter your name: ")
passw = getpass("Enter your password: ")

c = hda.Client(hda.Configuration(user=user, password=passw), progress=True, max_workers=1)


# ## Input *Data Query*
# 
# Masukkan parameter terkait dengan jenis data yang diinginkan serta lokasi dan waktunya.
# 
# `Dataset` adalah dataset-id. Untuk Sentinel-3 OLCI, value yang tersedia adalah sebagai berikut:
# 
# - `EO:EUM:DAT:SENTINEL-3:0556` &rarr; **2016-04-25** -- **28-04-2021**
# - `EO:EUM:DAT:SENTINEL-3:OL_2_WFR___` &rarr; **2021-04-29** -- **2023-12-31**
# 
# Sentinel-3 tersedia dalam 2 jenis satelit, `Sentinel-3A` dan `Sentinel-3B`. Jika pilihan ini tidak diisi, pada `query` akan terpilih semua satelit. Perlu dicatat bahwa Sentinel-3B tersedia mulai tanggal **2018-05-18**.

# In[ ]:





# In[ ]:


# Satellite parameter
print(
    Markdown("Please enter the :artificial_satellite: satellite parameters. For satellite ID, enter `1` to choose `EO:EUM:DAT:SENTINEL-3:0556` and `2` to choose `EO:EUM:DAT:SENTINEL-3:OL_2_WFR___`.")
)

while True:
    sat_id = int(input('Satellite ID: '))

    if sat_id == 1:
        dataset_id = 'EO:EUM:DAT:SENTINEL-3:0556'
        print('Dataset ID: ', dataset_id)
        break
    elif sat_id == 2:
        dataset_id = 'EO:EUM:DAT:SENTINEL-3:OL_2_WFR___'
        print('Dataset ID', dataset_id)
        break
    else:
        print("You put wrong number. Please try again!")


# In[ ]:


print(
    Markdown("For satellite name, enter `a` to choose `Sentinel-3A` and `b` to choose `Sentinel-3B`. Leave it blank if you want both Sentinel-3A and Sentinel-3B queried. Please note that Sentinel-3B id only available from 18 May 2018")
)

sat_nm = input("Satellite name: ")

if sat_nm == 'a':
    sat = 'Sentinel-3A'
    print('Satellite: ', sat)
elif sat_nm == 'b':
    sat = 'Sentinel-3B'
    print('Satellite: ', sat)
else:
    sat = ''
    print('Both Sentinel-3A and Sentinel-3B will be queried.')



# In[ ]:


# Area of interest
print('Please input your :earth_asia-text: area of interest. The coordinates should be in [bold yellow]decimal format[/bold yellow] with :heavy_minus_sign-text: sign for south-of-equator latitude or west-of-greenwich longitude')

north = input('North point: ') # -6.85
south = input('South point: ') # -7.95
west = input('West point: ') # 112.66
east = input('East point: ') # 114.65

bbox = [west, south, east, north]
extent = [west, east, north, south]
bbox_str = f'{west},{east},{south},{north}' 

bbox_polygon = geometry.Polygon(((west,south), (west,north), (east,north), (east,south)))


# In[ ]:


## Time of interest
print("Please input your :spiral_calendar-text: [u]date of interest[/u]. The dates should be in [bold yellow]YYYY-MM-DD[/bold yellow] format.")
print()
dtstart = input('Time start: ')
dtend = input('Time end: ')


# In[ ]:


query = {
  "dataset_id": dataset_id, 
  "dtstart": dtstart,
  "dtend": dtend,
  "bbox": bbox,
  "sat": sat,
  "type": "OL_2_WFR___",
  "timeliness": "NT",
  "itemsPerPage": 200,
  "startIndex": 0
}


# In[ ]:


search_result = c.search(query)
print(search_result)


# In[ ]:


from tqdm.auto import tqdm

for index, res in tqdm(enumerate(search_result.results, start=0), desc='Processed', total=len(search_result.results)):
    file_id = res['id']
#    print(index)
    start = datetime.strptime(res['properties']['startdate'], '%Y-%m-%dT%H:%M:%S%fZ')
    end = datetime.strptime(res['properties']['enddate'], '%Y-%m-%dT%H:%M:%S%fZ')
    timestamp = start + (end - start) / 2

    search_result[index].download()

    with zipfile.ZipFile(file_id + '.zip', 'r') as zip_ref:
        zip_ref.extractall(download_dir)
        print(f'Unzipping of product {file_id} finished.')
        os.remove(file_id + '.zip')

    filedir = os.path.join(download_dir, file_id)
    geo_coords = xr.open_dataset(filedir + '/geo_coordinates.nc')
    lon = geo_coords.variables['longitude'].data
    lat = geo_coords.variables['latitude'].data

    flag_file = xr.open_dataset(filedir + '/wqsf.nc')
    flag_names = flag_file['WQSF'].flag_meanings.split(' ') #flag names
    flag_vals = flag_file['WQSF'].flag_masks #flag bit values
    flags_data = flag_file.variables['WQSF'].data
    
    chlnn = xr.open_dataset(filedir + '/chl_nn.nc')
    chloc = xr.open_dataset(filedir + '/chl_oc4me.nc')
    tsmnn = xr.open_dataset(filedir + '/tsm_nn.nc')
    
    geo_file = xr.combine_by_coords([chlnn, chloc, tsmnn], join="exact", combine_attrs="drop_conflicts")
    chl_nn = geo_file.variables['CHL_NN'].data

    ref_file = xr.open_mfdataset(filedir + '/*reflectance.nc')
    
    flag_mask = flag_data_fast(list_flag_nn, flag_names, flag_vals, flags_data, flag_type='WQSF') # return a numpy array with selected flags
    chl_flagged = np.where(flag_mask, np.nan, chl_nn) # return a numpy array of masked chl-a data

    dta = xr.Dataset()
    
    dta['longitude'] = xr.DataArray(lon, dims=('rows','columns'))
    dta['longitude'].attrs = geo_coords['longitude'].attrs
    dta['latitude'] = xr.DataArray(lat, dims=('rows','columns'))
    dta['latitude'].attrs = geo_coords['latitude'].attrs
    
    dta['chl_flag'] = xr.DataArray(chl_flagged, dims=('rows','columns'))
    dta['chl_flag'].attrs = geo_file['CHL_NN'].attrs
    dta['chl_nn'] = xr.DataArray(chl_nn, dims=('rows','columns'))
    dta['chl_nn'].attrs = geo_file['CHL_NN'].attrs
    
    dta = dta.set_coords(['longitude','latitude'])
    
    dta = dta.expand_dims(dim={"time":[timestamp]}, axis=0)

    reggridded = cdo.sellonlatbox(bbox_str, input = dta, returnXDataset = True)
    reggridded.to_netcdf(os.path.join(result_dir , file_id + '.nc'))

    cdo.cleanTempDir()
    for allitem in os.listdir(download_dir):
        path = os.path.join(download_dir,allitem)
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    del geo_coords
    del geo_file
    del flag_file
    del dta

    gc.collect()


# 

# filtered_result = []
# 
# for res in search_result.results:
#     file_geom = shape(res['geometry'])
#     if bbox_polygon_shape.within(file_geom):
#         file_id = res['id']
#         filtered_result.append(res)
# #        print(f"Found: {file_id}")
# 
# print(len(filtered_result))
# 

# for res in search_result.results:
#     file_id = res['id']
#     print(f"Found: {file_id}")

# data_id = search_result[0].results[0]['id']
# 
# start = datetime.strptime(search_result[0].results[0]['properties']['startdate'], '%Y-%m-%dT%H:%M:%S%fZ')
# end = datetime.strptime(search_result[0].results[0]['properties']['enddate'], '%Y-%m-%dT%H:%M:%S%fZ')
# 
# timestamp = start + (end - start) / 2
# 
# print(start, end, timestamp)
# search_result[0].download()

# with zipfile.ZipFile(data_id + '.zip', 'r') as zip_ref:
#     zip_ref.extractall(download_dir)
#     print(f'Unzipping of product {data_id} finished.')
#     os.remove(data_id + '.zip')

# filedir = os.path.join(download_dir,data_id)
# geo_coords = xr.open_dataset(filedir + '/geo_coordinates.nc')
# flag_file = xr.open_dataset(filedir + '/wqsf.nc')
# 
# chlnn = xr.open_dataset(filedir + '/chl_nn.nc')
# chloc = xr.open_dataset(filedir + '/chl_oc4me.nc')
# tsmnn = xr.open_dataset(filedir + '/tsm_nn.nc')
# 
# geo_file = xr.combine_by_coords([chlnn, chloc, tsmnn], join="exact", combine_attrs="drop_conflicts")
# ref_file = xr.open_mfdataset(filedir + '/*reflectance.nc')

# lon = geo_coords.variables['longitude'].data
# lat = geo_coords.variables['latitude'].data
# flags_data = flag_file.variables['WQSF'].data
# chl_nn = geo_file.variables['CHL_NN'].data

# list_flag_nn = ['LAND', 'INLAND_WATER', 'TIDAL', 'COASTLINE', 'CLOUD', 'CLOUD_AMBIGUOUS', 'CLOUD_MARGIN', 'INVALID', 'COSMETIC', 'SATURATED', 'SUSPECT', 'HISOLZEN', 'HIGHGLINT', 'SNOW_ICE', 'AC_FAIL', 'WHITECAPS', 'ADJAC', 'RWNEG_O2', 'RWNEG_O3', 'RWNEG_O4', 'RWNEG_O5', 'RWNEG_O6', 'RWNEG_O7', 'RWNEG_O8', 'OCNN_FAIL']
# 
# flag_names = flag_file['WQSF'].flag_meanings.split(' ') #flag names
# flag_vals = flag_file['WQSF'].flag_masks #flag bit values
# flags_data = flag_file.variables['WQSF'].data
# 
# flag_mask = flag_data_fast(list_flag_nn, flag_names, flag_vals, flags_data, flag_type='WQSF') # return a numpy array with selected flags
# 
# chl_flagged = np.where(flag_mask, np.nan, chl_nn) # return a numpy array of masked chl-a data

# dta = xr.Dataset()
# 
# dta['longitude'] = xr.DataArray(lon, dims=('rows','columns'))
# dta['longitude'].attrs = geo_coords['longitude'].attrs
# dta['latitude'] = xr.DataArray(lat, dims=('rows','columns'))
# dta['latitude'].attrs = geo_coords['latitude'].attrs
# 
# dta['chl_flag'] = xr.DataArray(chl_flagged, dims=('rows','columns'))
# dta['CHL_NN'] = geo_file['CHL_NN']
# dta['chl_flag'].attrs = geo_file['CHL_NN'].attrs
# 
# dta = dta.set_coords(['longitude','latitude'])
# 
# dta = dta.expand_dims(dim={"time":[timestamp]}, axis=0)

# del geo_coords
# del geo_file
# del flag_file
# 
# gc.collect()

# chl_plot = 10 ** dta['chl_flag']
# asl_plot = 10 ** dta['CHL_NN']

# fig, ax = plt.subplots(figsize=[8,6], ncols = 2, layout='constrained', subplot_kw=dict(projection=ccrs.Robinson(central_longitude=112.0)))
# 
# for i in range(2):
#     ax[i].coastlines()
#     ini = ax[i].gridlines(draw_labels = True, alpha=0.5)
#     ini.top_labels = False
#     ini.right_labels = False
#     if not i == 0:
#         ini.left_labels = False
# 
# asl_plot.plot(ax=ax[0], x='longitude',y='latitude', add_colorbar=False, norm=colors.LogNorm(0.01,100), cmap=cmo.algae, transform=ccrs.PlateCarree(), zorder=0)
# ax[0].set_title("Before Applying Flags")
# chl_plot.plot(ax=ax[1], x='longitude',y='latitude', add_colorbar=False, norm=colors.LogNorm(0.01,100), cmap=cmo.algae, transform=ccrs.PlateCarree(), zorder=0)
# ax[1].set_title("After Applying Flags")
# 
# cbar = plt.colorbar(cm.ScalarMappable(norm=colors.LogNorm(0.01,100), cmap=cmo.algae), shrink=0.7, aspect=40, pad=0.02, orientation = 'horizontal', label = 'Chlorophyll-a Concentration',ax=ax[0:])

# reggridded = cdo.sellonlatbox(bbox_str, input = dta, returnXDataset = True)
# 
# # reggridded = cdo.remapcon(gridfile, input = bounded_dataset, returnXDataset = True)

# reggridded.to_netcdf(os.path.join(result_dir , data_id + '.nc'))
# 
# regrid = xr.open_dataset(os.path.join(result_dir , data_id + '.nc'))
# 
# print(regrid)

# chl_plot = 10 ** regrid['chl_flag']

# import cartopy
# 
# fig, ax = plt.subplots(figsize=[8,6], layout='constrained', subplot_kw=dict(projection=ccrs.Robinson(central_longitude=112.0)))
# 
# ax.set_extent(extent, crs=ccrs.PlateCarree())
# ax.add_feature(cf.LAND.with_scale('10m'), facecolor = 'beige', edgecolor='black', zorder = 1)
# #ax.coastlines()
# ini = ax.gridlines(draw_labels = True, alpha=0.5)
# ini.top_labels = False
# ini.right_labels = False
# 
# chl_plot.plot(ax=ax, x='longitude', y='latitude', norm=colors.LogNorm(0.01,100), cmap=cmo.algae, transform=ccrs.PlateCarree(), zorder=0)

# cdo.cleanTempDir()
# gc.collect()

# shutil.rmtree(download_dir)

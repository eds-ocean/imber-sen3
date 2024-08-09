# Sentinel-3 OLCI Marine Biogeochemistry Data Acquisition Program

<details>
<summary>📝 Integrated Marine Biosphere Research Group - Research Centre for Oceanography BRIN</summary>

&nbsp;

| Member Name | Member Name | 
|:-------------|:-------------|
| Faisal Hamzah | A'an J. Wahyudi |
| Idha Yulia Ikhsani | Afdal |
| Lestari | Rachma Puspitasari |
| Harmesa | Hanif Budi Prayitno |
| 👨‍🔬 **_Edwards Taufiqurrahman_**  | Ita Wulandari |
| Suci Lastrini | M. T. Kaisupy |

</details>

# Introduction

## Background
## Program Overview

This program created by combining various methods to access, subset, and combine Sentinel-3 netcdf datasets. This include using `xarray` to open and save `netcdf` dataset, using function provided by ... to apply flags, and using `CDO` (link to cdo) to subset and regrid dataset. The flowchart of the process is shown below.

```mermaid
flowchart TD;
A([ Start ])
B[/ Input location \n of interest. /]
C[/ Input time \n of interest. /]
D[Data selected and indexed \n based on input]
E[Apply Sentinel-3 OLCI \n recommended flags]

F(( ))
G(( ))
H(( ))
I(( ))

J[ Subsetting to location \n of interest ]
K{ All indexed dataset \n processed }
L[ Concatenate data \n by time index ]
M[ Save data ]
N([ End ])

      A-->B-->C-->F;
      G-->D-->E-->J-->K--NO-->D;
      K--YES-->H;
      I-->L-->M-->N

```

There are two version of this program: PlanetaryComputer and WEkEO version. Differences between these version are:

| Parameter         | Planetary Computer version      | Wekeo version                | 
|-------------------|---------------------------------|------------------------------|  
| Data source       | Planetary Computer by Microsoft | WEkEO by ESA's Copernicus    |
| Access method     | STAC                            | Harmonized Data Access (HDA) |
| Processing speed  | Very fast                       | Slow                         |
| Data availability | Incomplete                    | Complete                     |
| Credential required | No | Yes|


As the user, you can choose your preferable methods. For faster process, choose PlanetaryComputer version; but for data completeness you can choose WEkEO version. 

Please note that WEkEO requires credential to access their data. If you not yet have WEkEO account, you can create one for free [here](https://www.wekeo.eu/register).

## Pre-requisites

This program written in Python with dependency to following modules:

- aiohttp
- bottleneck
- cartopy
- cf_xarray
- colormaps
- dask
- h5netcdf
- ipykernel
- matplotlib
- netcdf4
- numpy
- planetary-computer
- pystac-client
- python-cdo
- requests
- rich
- rioxarray
- tqdm
- hda (available in `pip`)

If you are using Anaconda, you can use the provided `sen3_env.yml` file available in the `Settings` directory to create a new environment. Use command below in your terminal,

```terminal
conda env create -f sen3_env.yml
```

After its done, then you can enter the newly created environment and run the code.

# How To Use the Code

Basically, all you need is to run the file `Mode_1_PlanetaryComputer.py` and `Mode_2_WEkEO.py` from `Code` directory in your working environment. Copy the file to your working directory, enter the `sen3_env` Python environment, and lastly you can type command below in your terminal tu run it. 

```terminal
python Mode_1_PlanetaryComputer.py
```

Follow the instructions in the running program to add your location and time of interest. 

Below we provide simple explanation on how to use the code in certain environment.

_tbc_

## Via Github Codespaces
## Via Google Colab
## Via Other Cloud/Local Platform
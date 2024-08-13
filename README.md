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
| Processing speed  | Fast                       | Slow                         |
| Data availability | Incomplete                    | Complete                     |
| Credential required | No | Yes|


As the user, you can choose your preferred version. For faster process, choose PlanetaryComputer version; but for data completeness you can choose WEkEO version. 

Please note that WEkEO requires credential to access their data. If you not yet have WEkEO account, you can create one for free [here](https://www.wekeo.eu/register).

## Pre-requisites

This program written in Python with dependency on following modules:

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

If you are using Anaconda, you can use the provided `sen3_env.yml` file available in the `Settings` directory to create a new environment. Use command below in your terminal to setup the environment,

```terminal
conda env create -f sen3_env.yml
```

After the setup done, you can run the program from inside the environment.

# How To Use the Program

1. Copy the `Mode_1_PlanetaryComputer.py` and/or `Mode_2_WEkEO.py` file from `Code` directory to your own working directory,
2. Enter the `sen3_env` Python environment, 
3. Run the file 


```terminal
python Mode_1_PlanetaryComputer.py # if using PlanetaryComputer
python Mode_2_WEkEO.py # if using WEKEO

```

4. Then follow the instructions in the program. 


## Example for certain platform

Below we provide simple explanation on how to use the code in certain cloud platforms.

### Via Github Codespaces

Github codespace is a powerfull cloud programming tool provided by Github. We recommend you to use this as it is much easier than others. All you need:

1. Fork or clone this repository to your own Github,
2. Create Github codespace in forked/cloned repository (recommendation for codespace setup: Use 4 core and 16GB of RAM)
3. Install required modules,
4. Run the program.
5. Download the result to your local computer.

### Via Google Colab

Google Colab is another powerfull tools. The advantage of using it is that you can copy the result to your own Google Drive storage. The step is easy too:

1. Clone this repository to Google Colab (by using `git` or download this repository zip file),
2. Install required modules using `pip`
3. Run the program
4. Download the result, or copy it to your Google Drive.

![Video](Docs/running_program.webm)
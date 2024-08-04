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

## Introduction

### Sentinel-3 Data Access

![alt text](image-1.png)

### Pre-requisites

This program is intended to be used in a cloud environment e.g. JupyterHub or Github Codespaces. However, you can also run the code in your local machine.

Please make sure that your cloud or local machine can connect to global internet. For example, you cannot run it in an HPC with access only to local intranet.

In your working machine, you will need to install required modules. Conda environment's yml file is available in `Settings` directory.

## How To

### First: Copy this repo

Go to `Code` button and find the link to copy this repository (or download the zip file) to your preferred machine. If you are using Github, you can just fork this repo. Go to `https://github.com/eds-ocean/imber-sen3` and click **Fork** button, then continue with the instruction.

If you are not using github, you might want to download the zip file to your local computer, then upload and extract it on your JupyterHub.

Detailed information of each tep shown below.

### Using WEkEO JupyterHub

1. Log in to your Wekeo account ([create account here](https://www.wekeo.eu/register){:target="_blank"} if you don't have it yet).
2. Click the logo on upper right side and choose "Jupyter Notebook"
3. Add your credential to log in.
4. Choose one of server. It recommended to choose "Earth Observation Tools". 

After successfully log in to Jupyter Notebook, you can now upload the downloaded zip file from Github.

1. In the right sidebar, choose "Upload"
2. Open new Terminal 
3. Unzip the file using terminal

    ```bash
    unzip unzip imber-sen3-main.zip
    ```

    ![alt text](<Screenshot from 2024-08-04 14-13-06.png>)

### Using Github Codespace

After you're done forking this repo, you can now create codespace to run the code. Go to the forked repo, click the greed `Code` button then click Codespace. 

You might want setup the codespace first. To do so, in the Codespace tab click 3-dot (`...`) button and then choose "Manage Codespace" In the right, there is green button and click on left right side of the button (the thing with arrow), then select "Configure and create codespace". Fill the form like below.

![alt text](image.png)


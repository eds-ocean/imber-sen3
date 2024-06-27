# Simplifikasi proses akuisisi data Sentinel-3 OLCI Level 2

#### Oleh: Kelompok riset IMBeR - PRO BRIN

## Pendahuluan



## Modul dan List Kebutuhan
Untuk menggunakan _script_ ini, diperlukan beberapa hal berikut:

1. Lingkungan (_environment_) pengerjaan.
   Kedua script ini dimaksudkan untuk mengurangi kebutuhan bandwidth internet yang digunakan oleh komputer lokal namun juga tidak memberikan beban bagi platform cloud. Script yang disediakan disarankan untuk dijalankan di lingkungan _cloud_ dengan _environment_ JupyterHub, misalnya yang disediakan oleh WeKeo dan Copernicus.

   Script pertama menggunakan data yang ditaruh di sistem [Planetary Computer yang disediakan oleh Microsoft](https://planetarycomputer.microsoft.com/). Data ini dapat diakses secara gratis dan tidak diperlukan otentifikasi untuk menggunakannya. Sangat disarankan untuk menuliskan Planetary Computer sebagai sumber akses data.

   Script kedua menggunakan data yang disediakan oleh [WeKeo](https://www.wekeo.eu/) dan diakses dengan [_Harmonized Data Access (HDA)_](https://help.wekeo.eu/en/collections/3530725-wekeo-data-download). Untuk mengakses data dari WeKeo ini, autentikasi diperlukan. Username dan password dapat diperoleh dengan meregistrasi akun di website WeKeo.
   
3. Modul Python.
4. Lokasi dan waktu yang diperlukan
5. Parameter yang diperlukan.

## Cara Kerja

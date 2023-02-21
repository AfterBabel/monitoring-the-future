# Monitoring the Future database

## Pre-requisites

* Install [Anaconda](https://www.anaconda.com/products/distribution)
* `conda activate`

## Steps

The following steps will produce a `db.csv` file containing all the data from all Monitoring the Future surveys since the 1970s (~2.7M rows and ~4.6k columns).

* Get session id: 
    * Log in to the [Monitoring the Future](https://www.icpsr.umich.edu/web/NAHDAP/series/35) website in Chrome browser
    * Open Chrome Developer Tools 
    * Application > Storage > Cookies
    * Filter by "JSESSIONID"
    * Copy the first one
* `git clone <this repo>`
* `cd <this repo>`
* Download files: `./download.sh SESSIONID`
* `cd files`
* Unzip: `ls | xargs -I{} unzip {}`
* Back to root of repo: `cd ..`
* Merge the data: `python script.py`
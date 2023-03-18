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
* Make metadata: `python make_metadata.py`. This will produce two files: `datasets.tsv` and `variables.tsv`.
* Copy-paste columns `irn`, `variable_name`, and `form` from [this spreadsheet](https://docs.google.com/spreadsheets/d/1z-RUnXtbaFWtZdznlrhjud41e6Iz74cBJaUh8nPrx8M/edit?usp=sharing) into a file named `selected_variables.tsv`
* Make db: `python make_db.py >> log.txt`:
    * This will produce one file per (grade, form) combination in the format `grade-{grade}_form-{form}.csv`
    * The log produced will displays:
        * The fuzzy matching done for certain variables
        * The unmatched variables for certain datasets -> This may be expected as a form might be missing some variables in some years
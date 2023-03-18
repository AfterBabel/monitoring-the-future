# Monitoring the Future database

## Pre-requisites

* Install [Anaconda](https://www.anaconda.com/products/distribution)
* `conda activate`

## Steps

The following steps will produce a series of CSV DB files for a specific grade and Monitoring the Future survey form for all years.

1. Get session id: 
    * Log in to the [Monitoring the Future](https://www.icpsr.umich.edu/web/NAHDAP/series/35) website in Chrome browser
    * Open Chrome Developer Tools 
    * Application > Storage > Cookies
    * Filter by "JSESSIONID"
    * Copy the first one
2. `git clone <this repo>`
3. `cd <this repo>`
4. Download files: `./download.sh SESSIONID`
5. `cd files`
6. Unzip: `ls | xargs -I{} unzip {}`
7. Back to root of repo: `cd ..`
8. Make metadata: `python make_metadata.py`. This will produce two files: `datasets.tsv` and `variables.tsv`.
9. Copy-paste columns `irn`, `variable_name`, and `form` from [this spreadsheet](https://docs.google.com/spreadsheets/d/1z-RUnXtbaFWtZdznlrhjud41e6Iz74cBJaUh8nPrx8M/edit?usp=sharing) into a file named `selected_variables.tsv`
10. Make db: `python make_db.py >> log.txt`:
    * This will produce one file per (grade, form) combination in the format `grade-{grade}_form-{form}.csv`
    * The log produced will displays:
        * The fuzzy matching done for certain variables
        * The unmatched variables for certain datasets -> This may be expected as a form might be missing some variables in some years
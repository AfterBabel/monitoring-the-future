# Monitoring the Future database

## Pre-requisites

* Install Anaconda
* `conda activate`
* `pip install pyreadstat`

## Steps

* Get session id: 
    * Log in to the UMich website in Chrome browser
    * Open Chrome Developer Tools 
    * Application > Storage > Cookies
    * Filter by "JSESSIONID"
    * Copy the first one
* Download files: `./download.sh SESSIONID`
* `cd files`
* Unzip: `ls | xargs -I{} unzip {}`
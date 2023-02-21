rm -rf files

curl "https://www.icpsr.umich.edu/web/NAHDAP/series/35?start=0&sort=TITLE_SORT%20asc&SERIESQ=35&ARCHIVE=NAHDAP&rows=100" \
    | grep 'variables.searchResults' \
    | sed 's/variables.searchResults = \(.*\);/\1/g' \
    | tee response.json \
    | jq '.response.docs[] | .ID' \
    | xargs -I{} curl 'https://www.icpsr.umich.edu/web/NAHDAP/studies/{}' \
    | grep '{"funder"' \
    | sed 's/\(.*\);/\1/g' \
    > studies.json

mkdir files

# Downloading by chunks of 10 is necessary because the curl command returns a temporary url to perform the download
# and if you are processing a long list of temporary urls, by the time you get to the end of it, the temporary urls
# will have expired. Processing chunks of 10 ensures the temporary urls do not get stale.
for start in `seq 0 10 70`;
do
    tail -n+$start studies.json | head -n10 \
    | jq '.distribution[] | select(.fileFormat=="Stata") | .contentURL' \
    | xargs -I{} curl {} -H "Cookie: JSESSIONID=$1;" \
    | grep performDownload | sed 's/https/\nhttps/g' | grep ^https | sed 's/\(^https[^ <]*\)"\(.*\)/\1/g' | uniq \
    | xargs wget -P files
done
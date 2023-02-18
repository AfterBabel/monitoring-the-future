curl 'https://www.icpsr.umich.edu/web/NAHDAP/series/35?start=0&sort=TITLE_SORT%20asc&SERIESQ=35&ARCHIVE=NAHDAP&rows=100' \
    | grep 'variables.searchResults' \
    | sed 's/variables.searchResults = \(.*\);/\1/g' \
    | tee response.json \
    | jq '.response.docs[] | .ID' \
    | xargs -I{} curl 'https://www.icpsr.umich.edu/web/NAHDAP/studies/{}' \
    | grep '{"funder"' \
    | sed 's/\(.*\);/\1/g' \
    | tee studies.json \
    | jq '.distribution[] | select(.fileFormat=="SPSS") | .contentURL' \
    | xargs -I{} curl {} -H 'Cookie: JSESSIONID=$1;' \
    | grep performDownload | sed 's/https/\nhttps/g' | grep ^https | sed 's/\(^https[^ <]*\)"\(.*\)/\1/g' | uniq \
    | xargs wget -P files
#!/bin/bash

if [[ $# != 3 ]]; then
    echo "Usage: ./killscans.sh <platform> <scannerid> <scan title matcher>"
    echo 'Note: we expect APIKEY and APISEC to be defined in $HOME/.$PLAT.apikeys'
    echo
    echo "<scannerid> corresponds to the internal nessus id for the scanner, which can be seen at"
    echo "the end of the URL, for example when viewing the details of the scanner."
    echo
    echo "e.g.: https://us-1a.svc.nessus.org/nessus6.html#/settings/scanners/linked/285"
    echo
    echo "The id 285 represents scanner01 in us-1a"
    echo
    echo "<scan title matcher> means any portion of the title to match on"
    echo "For security center scans, that look like: 0d85820c-4faf-54b0-84ff-f4d9c76c3bf3-1008179/Chunk 355"
    echo "Usually the first set of characters is enough, i.e.: 0d85820c"
    exit 1
fi

PLAT=$1
SCANNER=$2
SCAN=$3

source ~/.${PLAT}.apikeys

if [ -z "$SCANNER" ]; then
    echo "no scanner"
    exit 1
fi

echo "Using $PLAT $SCANNER $SCAN"

for a in $(curl -H "X-ApiKeys: accessKey=$APIKEY; secretKey=$APISEC" https://${PLAT}.svc.nessus.org/scanners/$SCANNER/scans | jq '.scans[] | .id +" " + .name' | tr -d '"' | grep $SCAN | awk '{print $1}'); do
    echo $a;
    curl -X POST -d '{"action":"stop"}' -H 'Content-Type: application/json' -H "X-ApiKeys: accessKey=$APIKEY; secretKey=$APISEC" "https://${PLAT}.svc.nessus.org/scanners/$SCANNER/scans/$a/control"
done

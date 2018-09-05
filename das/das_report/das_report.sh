#!/bin/bash
## Report connected DAS' and their state

## Basic Setup - Source ax_vars from /usr/local/axcient

. /usr/local/axcient/ax_vars

std_width="%-10s %-10s %-10s %-15s %-30s"
std_red="${red}${std_width}${endcolor}"

printf "${std_width}\n" "STATION" "SVCID" "DEV" "SIZE" "STATE"
echo "----------------------------------------------------------"
for station in $DAS_STATIONS
    do
        conn_var=$(ssh -o ConnectTimeout=5 $station "cat | /bin/bash /dev/stdin ${station}" < /usr/local/axcient/das_report/collect_das.sh 2>/dev/null)
        if [ $? -eq 0 ]; then
            printf "${std_width}\n" "$conn_var"
        else
            printf "${std_red}\n" "${station}" "NA" "NA" "ERROR"
        fi
done

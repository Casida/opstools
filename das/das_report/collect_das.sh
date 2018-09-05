#!/bin/bash
station=$1
red='\e[0;31m'
ltblue='\e[1;34m'
endcolor='\e[0m'
std_width="%-10s %-10s %-10s %-15s %-30s"
std_blue="${ltblue}${std_width}${endcolor}"
DAS_LIST=$(ls /dev/ax)
for das in $DAS_LIST
    do  
        DEV_ID=$(readlink /dev/ax/$das)
        SVCID=$(readlink /dev/ax/.dasids/$das)
        DEV_SZ=$(df -h /dev/ax/$das | tail -1 | awk -F" " '{print $3}')
        if [ -f /uptiva/replicator/$SVCID/completions ]; then
            COMPLETE_DATE=$(date -d @$(awk '{print $1}' /uptiva/replicator/$SVCID/completions) +"%F %T")
            printf "${std_blue}\n" "$station" "$SVCID" "$DEV_ID" "$DEV_SZ" "$COMPLETE_DATE"
        elif [ -d /uptiva/replicator/$SVCID ]; then
            COMPLETE_DATE="In Process"
            printf "${std_width}\n" "$station" "$SVCID" "$DEV_ID" "$DEV_SZ" "$COMPLETE_DATE"
        else
            COMPLETE_DATE="Detached"
            printf "${std_blue}\n" "$station" "$SVCID" "$DEV_ID" "$DEV_SZ" "$COMPLETE_DATE"
        fi  
done

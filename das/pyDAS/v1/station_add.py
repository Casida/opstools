#!/usr/bin/python

# Use this script to add, remove, and update (eventually) das stations

import das_util as du
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-a', '--ipaddr', dest="ip", action="store", help="Station IP address")
parser.add_option('-p', '--ports', dest="ports", action="store", help="Number of USB ports including connected hubs")
parser.add_option('-l', '--location', dest="location", action="store", help="Physical location of the DAS station")
parser.add_option('-b', '--hub', dest="hub", action="store_true", help="Does this station have a connected USB Hub?")

options, remainder = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

usb_slots = 100
usb_hub = 0
if options.hub:
    usb_hub = 1

db = du.DasDB()
db.station_add(options.ip, options.ports, usb_hub, usb_slots, options.location)

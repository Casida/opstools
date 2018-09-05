#!/usr/bin/python

import das_util as du
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-s', '--svcid', dest="svcid", action="store", help="Service ID of DAS. eg. a53o")
parser.add_option('-d', '--dasid', dest="dasid", action="store", help="DAS ID of DAS on station. eg: das0")
parser.add_option('-v', '--device', dest="dev_name", action="store", help="Full path of linux device for DAS")
parser.add_option('-r', '--serial', dest="dev_serial", action="store", help="Serial number of DAS")
parser.add_option('-p', '--purpose', dest="dev_purpose", action="store", help="DAS Purpose string")

options, remainder = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

if options.dev_name:
    dev_base = du.get_dev_base(options.dev_name)

if du.get_pid(options.svcid):
    print "Can't add, already existing pid"
    sys.exit(1)

db = du.DasDB()
instID = db.device_attach(options.svcid, options.dasid, options.dev_name, options.dev_serial, options.dev_purpose)

# Store instance ID in /var/cache/das...
du.set_pid(options.svcid, instID)

# Find all the flags
flagList = db.flag_list(options.svcid)
if len(flagList) > 0:
    db.flag_assign(flagList, instID)
db.close()
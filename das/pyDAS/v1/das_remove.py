#!/usr/bin/python

import das_util as du
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-s', '--svcid', dest="svcid", action="store", help="Service ID of DAS. eg. a53o")

options, remainder = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

db = du.DasDB()
db.device_detach(options.svcid)
db.close()

du.clear_pid(options.svcid)
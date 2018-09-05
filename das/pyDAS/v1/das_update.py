#!/usr/bin/python

import das_util as du
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-s', '--svcid', dest="svcid", action="store", help="Service ID of DAS. eg. a53o")
parser.add_option('-p', '--port', dest="port", action="store", help="Replication port. eg. 4019")
parser.add_option('-b', '--begin', dest="begin", action="store_true", help="Start replication")
parser.add_option('-f', '--finish', dest="finish", action="store_true", help="Finish replication")

options, remainder = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

idList = []

if options.begin:
    db = du.DasDB()
    db.start_dev_replication(options.svcid, options.port)
    db.close()

if options.finish:
    db = du.DasDB()
    db.stop_dev_replication(options.svcid)
    db.close()
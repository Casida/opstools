#!/usr/bin/python

# Use this script to add, remove, and update das flags

import das_util as du
import optparse
import sys

def add_options(parser):
    parser.add_option('-i', '--id', dest="flag_id", action="store", help="Flag ID, used for updates")
    parser.add_option('-a', '--assign', dest="assign_id", action="store", help="Assign status_id to a list of flag_ids")
    parser.add_option('-d', '--deactivate', dest="deactivate", action="store_true", help="Deactivate flag_id")
    parser.add_option('-l', '--desc', dest="description", action="store", help="Optional long flag description")
    return

def main():
    parser = optparse.OptionParser()
    add_options(parser)
    options, args = parser.parse_args()

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    if options.assign_id:
        if len(args) == 2:
            print "Can't add new flags and assign at same time"
            parser.print_help()
            sys.exit(2)
        if options.flag_id:
            db = du.DasDB()
            db.flag_assign(options.flag_id, options.assign_id)
            db.close()
        else:
            print "Flag ID and Status ID are required for assignment"
            parser.print_help()
            sys.exit(1)

    if options.deactivate:
        if len(args) == 2:
            print "Can't add new flags and deactivate at same time"
            parser.print_help()
            sys.exit(2)
        if options.flag_id:
            db = du.DasDB()
            db.flag_deactivate(options.flag_id)
            db.close()
        else:
            print "Flag ID is required to deactivate"
            parser.print_help()
            sys.exit(1)

    if len(args) == 2:
        db = du.DasDB()
        service_id = args[0]
        flag_name = args[1]
        if options.description:
            db.flag_add(service_id, flag_name, options.description)
        else:
            db.flag_add(service_id, flag_name)
        db.close()
    return

if __name__ == "__main__":
    main()

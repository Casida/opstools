#!/usr/bin/python

import das_util as du
import optparse
import sys

parser = optparse.OptionParser()
parser.add_option('-s', '--svcid', dest="svcid", action="store", help="Service ID of DAS. eg. a53o")
parser.add_option('-i', '--initial', dest="initial", action="store_true", help="Initialize entries or update")
parser.add_option('-j', '--job', dest="job_name", action="store", help="Send a job")
parser.add_option('-b', '--begin', dest="begin", action="store_true", help="Mark a job as started. Requires -j")
parser.add_option('-x', '--end', dest="end", action="store_true", help="Mark a job as complete. Requires -j")

options, remainder = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

if not options.svcid:
    print "All options require a service ID"
    sys.exit(1)

if options.begin:
    if options.job_name:
        db = du.DasDB()
        jobId = db.get_job_id(options.job_name)
        if jobId > 0:
            db.job_start_replication(jobId, options.svcid)
        else:
            print "Job doesn't exist in joblist."
        db.close()
    else:
        print "Need a job name to start a job"
        sys.exit(1)

if options.end:
    if options.job_name:
        db = du.DasDB()
        jobId = db.get_job_id(options.job_name)
        if jobId > 0:
            db.job_stop_replication(jobId, options.svcid)
        else:
            print "Job doesn't exist in joblist."
        db.close()
    else:
        print "Need a job name to end a job"
        sys.exit(1)

if options.initial:
    db = du.DasDB()
    db.seed_jobs(options.svcid)
    db.close()
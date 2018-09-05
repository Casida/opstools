#!/usr/bin/python

import os
import sys
import simplejson as json
import time
import urllib2
import optparse

# API setup area
SECRET = 'Nope...No Secret Here'
API_URL = 'https://rmc02.axdc.lan/datacenter_api/das'
CACHE_DIR = '/var/cache/das'

usage = "usage: %prog [options] serviceId statusMessage"
parser = optparse.OptionParser(usage=usage)
parser.add_option('-i', '--initial', dest="initial", action="store_true", help="This is a new entry for the named DAS on this station")
parser.add_option('-u', '--update', dest="update", action="store_true", help="This is an update for the named DAS on this station")
parser.add_option('-r', '--remove', dest="remove", action="store_true", help="Use this option to set the named DAS as COMPLETE")
options, args = parser.parse_args()

if len(args) < 2:
    print "Service ID and Message are required"
    parser.print_help()
    sys.exit(1)

svcid = args[0]
message = args[1]

options_dict = vars(options)
for x in options_dict.keys():
    if options_dict[x] == None:
        del options_dict[x]
        
if len(options_dict) != 1:
    print "ERROR\n-i, -u, and -r are mutually exclusive\n"
    parser.print_help()
    sys.exit(1)

def rmc_update(SECRET, URL, content):
    req = urllib2.Request(URL, content)
    req.add_header('X_API_KEY', SECRET)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print "Got ERROR from RMC(%s): %s: Exiting with no changes" % (e.errno, e.strerror)
        sys.exit(1)
    das_id = json.loads(response.read())
    return das_id["das_status_id"]

if options_dict.has_key('initial'):
    data = json.dumps({"serviceId": svcid, "status": message, "startTime": int(time.time())})
    update_id = rmc_update(SECRET, API_URL, data)
    cache_path = "%s/%s.rmc" % (CACHE_DIR, args[0])
    try:
        inst_fh = open(cache_path, 'w+')
    except IOError, e:
        print "%s: %s" % (cache_path, e.strerror)
        print "I couldn't open %s, does /var/cache/das exist? Do you have permission to write there?" % (cache_path)
        sys.exit(1)
    inst_id = open(cache_path, 'w+')
    inst_id.write(str(update_id))
    inst_id.close()
    print "Adding DB Entry for %s: status: %s, database_id: %s, cache_file: %s" % (svcid, message, str(update_id), cache_path)

if options_dict.has_key('update'):
    cache_path = "%s/%s.rmc" % (CACHE_DIR, args[0])
    try:
        inst_fh = open(cache_path, 'r+')
    except IOError, e:
        print "%s: %s" % (cache_path, e.strerror)
        print "I couldn't find the named DAS in my records, was it initialized on this station?"
        sys.exit(1)
    inst_id = int(inst_fh.read())
    inst_fh.close()
    data = json.dumps({"serviceId": svcid, "status": message, "startTime": int(time.time()),"dasHistoryId": inst_id})
    update_id = rmc_update(SECRET, API_URL, data)
    print "Updating DB Entry for %s: status: %s, database_id: %s, cache_file: %s" % (svcid, message, str(update_id), cache_path)

if options_dict.has_key('remove'):
    cache_path = "%s/%s.rmc" % (CACHE_DIR, args[0])
    try:
        inst_fh = open(cache_path, 'r+')
    except IOError, e:
        print "%s: %s" % (cache_path, e.strerror)
        print "I couldn't find the named DAS in my records, was it initialized on this station?"
        sys.exit(1)
    inst_id = int(inst_fh.read())
    inst_fh.close()
    data = json.dumps({"serviceId": svcid, "status": message, "startTime": int(time.time()),"dasHistoryId": inst_id})
    update_id = rmc_update(SECRET, API_URL, data)
    print "Updating and removing cache file for DB Entry for %s: status: %s, database_id: %s, cache_file: %s" % (svcid, message, str(update_id), cache_path)
    os.remove(cache_path)

    

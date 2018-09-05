#!/usr/bin/env python

import os, boto3, requests, sys
from datadog import initialize, api
from ConfigParser import SafeConfigParser

# Grab DD api creds
parser = SafeConfigParser()
parser.read('config.ini')
api_key = parser.get('datadog', 'DD_API_KEY')
app_key = parser.get('datadog', 'DD_APP_KEY')

data = {
       'api_key': api_key,
       'application_key': app_key
       }

#datadog infastructure list with tags
url = "https://app.datadoghq.com/reports/v2/overview?metrics=avg%3Aaws.ec2.cpuutilization%2Cavg%3Aazure.vm.percentage_cpu%2Cavg%3Agcp.gce.instance.cpu.utilization%2Cavg%3Asystem.cpu.idle%2Cavg%3Asystem.cpu.iowait%2Cavg%3Asystem.load.norm.15%2Cavg%3Avsphere.cpu.usage&with_apps=true&with_sources=true&with_aliases=true&with_meta=true&with_mute_status=true&with_tags=true"

def main():
	tags = {} # dict of tags to iterate over and apply to DD
	regions = [] #list of aws regions
		
	#authenticate and get datadog json dump
	status,dd_hosts = get_dd_json(url,data)
	if status != 200: 
		sys.exit("Could not connect to datadog")

	#match up tags from aws and apply to DD hosts
	regions = get_regions()
	for region in regions:
		instanceList = []
		instanceList = get_instance_ids(region)
		for instanceID in instanceList:
			tags = get_aws_tags(instanceID)
			dd_hostname = parse_dd_json(instanceID, dd_hosts)
			if dd_hostname:
				apply_tags(dd_hostname,tags)
	sys.exit("Taggr-er is done")

def get_aws_tags(instanceID):
	'''
	Provide instanceID and get back dict of tags from AWS
	'''
	ec2 = boto3.resource('ec2')
	ec2instance = ec2.Instance(instanceID)
	tagDict = {}
	#include instanceID so we can search for it in DD
	tagDict['tags_provided_by'] = 'taggr-er'
	tagDict['instanceID'] = instanceID
	try:
		for tags in ec2instance.tags:
			if tags:
				tagDict[tags['Key']] = tags['Value']
	except:
		pass
	return tagDict

def parse_dd_json(instanceID,dd_hosts):
	'''
	Get datadog infastructure json dump because we can look up instance id and dd_hostname,
	the api cannot query by alias.
	'''
	hostname = None
	for line in dd_hosts['rows']:
		if 'aws_id' in line:
			if str(line['aws_id']) == str(instanceID):
				hostname = str(line['name'])
		if 'aliases' in line:
			for alias in line['aliases']:
				if alias == str(instanceID):
					hostname = str(line['name'])
	return hostname

def get_dd_json(url,data):
	'''
	Fetch json data with requests, returns status code and data
	'''
	r = requests.get(url, params=data, stream=True)
	r.raw.decode_content = True
	
	data = r.json()
	return (r.status_code,data)


def apply_tags(hostname,tags):
	'''
	Accepts hostname and a list of tags (key:value), applies them to datadog instance matches
	'''
	options = {'api_key': api_key,'app_key': app_key}
	initialize(**options)
	tag_list=[k+":"+v for k, v in tags.iteritems()]
	api.Tag.update(hostname, tags=tag_list)

def get_instance_ids(region):
	'''
	Get list of all running instance IDs in a region
	'''
	instanceList = []
	ec2client = boto3.client('ec2', region_name=region)
	response = ec2client.describe_instances()
	for reservation in response["Reservations"]:
		for instance in reservation["Instances"]:
			instanceList.append(instance["InstanceId"])
	return instanceList


def get_regions():
	'''
	Get all regions from aws
	'''
	regionList=[]
	ec2 = boto3.client('ec2')
	regions = ec2.describe_regions()
	for region in regions['Regions']:
		regionList.append(region['RegionName'])
	return regionList

if __name__ == '__main__':
	main()

#!/usr/bin/env python

import os, argparse, boto, boto.ec2, csv, sqlite3, requests
from datadog import initialize, api #remove data_dog_infastructure() and this won't be needed

#################
###CREDENTIALS###
#################
#AWS-PROD
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

#AWS-ENG
#AWS_ACCESS_KEY_ID_ENG = os.environ['AWS_ACCESS_KEY_ID_ENG']
#AWS_SECRET_ACCESS_KEY_ENG = os.environ['AWS_SECRET_ACCESS_KEY_ENG']

#DATADOG
DD_API_KEY = os.environ['DD_API_KEY']
DD_APP_KEY = os.environ['DD_APP_KEY']

###############
###FUNCTIONS###
###############
def main():
	#AWS
	print "Gathering AWS Inventory..."
	regions = get_aws_regions()
	for region in regions: 	#iterate through all aws regions
		region = str(region).replace("RegionInfo:","")
		try:
			aws_inv_list(region)
			#print region
		except:
			print region+": access issue, skipping (china, gov, etc)"
	#data dog
	print "Gathering Datadog Inventory..."
	data_dog_infastructure()

def aws_inv_list(region):
	ec2conn = boto.ec2.connect_to_region(region)
	#reservations = ec2conn.get_all_reservations() # what is the difference between reservation and instance?
	reservations = ec2conn.get_all_instances()	
	instances = [i for r in reservations for i in r.instances]
	for i in instances:
		i = i.__dict__
		
		try: awsName = i['tags']['Name']
		except: awsName = "NULL"

		try:
			if i['ip_address'] == None:
				ip_address = "NULL"
			else:
				ip_address = i['ip_address']
		except:
			ip_address = "NULL"

		try:
			if i['private_ip_address'] == None:
				internal_ip = "NULL"
			else:
				internal_ip = str(i['private_ip_address'])
		except:
			internal_ip = "NULL"
		sql_write("'"+i['id']+"'","'"+str(ip_address)+"'","'"+str(internal_ip)+"'","'"+awsName+"'","'"+str(region)+"'","'aws'")

def get_aws_regions(): #get live list of aws zones/regions
	regions = boto.ec2.regions()
	return regions

def data_dog_infastructure():
	options = {'api_key': DD_API_KEY,'app_key': DD_APP_KEY}
	initialize(**options)
	hosts = api.Infrastructure.search(q='hosts:')
	for host in hosts['results']['hosts']:
		region = "NULL"
		tags = api.Tag.get(host)
		for tag in tags['tags']:
			if 'region:' in tag:
				region = str(tag).replace("region:","")
		sql_write("NULL","NULL","NULL","'"+str(host)+"'","'"+str(region)+"'","'datadog'")

def check_db(db): # create db schema if db doesn't exist
	if not os.path.exists(db):
		with sqlite3.connect(db) as conn:
			print 'Creating sqlite db from schema...'
			with open('schema.sql', 'rt') as f:
				schema = f.read()
			conn.executescript(schema)

def sql_write(aws_instance_id,external_ip,internal_ip,aws_hostname,aws_region,reported_by):
	try:
		conn = sqlite3.connect(db_filename)
		cursor = conn.cursor()
		query = ('''insert into inventory ('aws_instance_id','external_ip','internal_ip','aws_hostname','aws_region','reported_by') values (%s,%s,%s,%s,%s,%s);''') % (aws_instance_id,external_ip,internal_ip,aws_hostname,aws_region,reported_by)
		cursor.execute(query)
		conn.commit()
		conn.close()
		return True
	except:
		print "Failed to write to sql: %s" % aws_hostname
		return False

def flush_db(db):
	with sqlite3.connect(db) as conn:
		print "Flushing db for fresh data..."
		cursor = conn.cursor()
		query = ('''delete from inventory;''') #flush the table
		cursor.execute(query)
		query = ('''vacuum;''') # clears unused space
		cursor.execute(query)
		conn.commit()

def sql(query): # sql to view records, pass query
	conn = sqlite3.connect(db_filename)
	cursor = conn.cursor()
	cursor.execute(query)
	data = cursor.fetchall()
	conn.close()
	return data

##########
###CODE###
##########

if __name__ == '__main__':
	db_filename = 'inv.db' #define db filename
	check_db(db_filename) # initize db
	#flush_db(db_filename) # flush db
	main()

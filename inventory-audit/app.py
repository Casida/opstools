#!/usr/bin/env python

from flask import Flask, render_template, jsonify, request
import sqlite3, os, re, csv
from ec2_inventory import check_db

###########
###FLASK###
###########
app = Flask(__name__) #start flask app

###############
###FUNCTIONS###
###############

@app.route('/') 
@app.route('/aws')
@app.route('/aws/<csv>')
def view_aws_dupes(csv=None):
	query = """
			select count(DISTINCT aws_instance_id) as count, aws_hostname, group_concat(DISTINCT aws_region) as aws_region
			from inventory
			where (aws_hostname != 'NULL' and aws_hostname is not NULL) 
			group by aws_hostname, aws_region
			having count(DISTINCT aws_instance_id) > 1
			order by count(DISTINCT aws_instance_id) DESC; 
			"""
	data = sql(query)
	if csv:
		csv_out("aws_dupes.csv",data)
	return render_template('inventory.html',data=data)

@app.route('/dd')
@app.route('/dd/<csv>') 
def view_dd_dupes(csv=None):
	query = """
			select count(DISTINCT i1.aws_hostname) as count,(coalesce(i1.aws_hostname,'') ||", "|| coalesce(i2.aws_hostname,'')) AS aws_hostname, '---' as 'aws_region'
			from inventory i1
			left join inventory i2 on i1.aws_hostname = replace(replace(replace(i2.aws_hostname,".cloud",""),".dcld",""),".prod","")
			where i2.aws_hostname like '%.cloud%' or i2.aws_hostname like '%.dcld%' or i2.aws_hostname like '%.prod%'
			group by i1.aws_hostname;
			"""
	data = sql(query)
	if csv:
		csv_out("dd_dupes.csv",data)
	return render_template('inventory.html',data=data)

@app.route('/dd-broken') #this is currently broken. sqlite does not support regex..... need to run through the data in python now.
def regex():
	query = """
			select count(DISTINCT i1.aws_hostname) as count,(coalesce(i1.aws_hostname,'') ||", "|| coalesce(i2.aws_hostname,'')) AS aws_hostname, '---' as 'aws_region'
			from inventory i1
			left join inventory i2 on i1.aws_hostname = REGEXP_REPLACE(i2.aws_hostname,'(\..*$)',"") 
			group by i1.aws_hostname;
			"""
	data = sql(query)
	return render_template('inventory.html',data=data)

@app.route('/invalid')
def invalid():
	query = """
			select count(DISTINCT aws_instance_id) as count, aws_hostname, group_concat(DISTINCT aws_region) as aws_region
			from inventory
			where (aws_hostname != 'NULL' and aws_hostname is not NULL) 
			group by aws_hostname
			having count(DISTINCT aws_instance_id) > 1
			order by count(DISTINCT aws_instance_id) DESC; 
			"""
	data = sql(query)
	return render_template('inventory.html',data=data)

@app.route('/ip_hosts')
@app.route('/ip_hosts/<csv>')
def ip_hostnames(csv=None):
	query = """
			select count(i2.internal_ip) AS count, (coalesce(i1.aws_hostname,'') ||", "|| COALESCE(i2.aws_hostname,'')) as hostname, i2.aws_region
			from inventory i1
			left join inventory i2 on replace(replace(i1.aws_hostname,"ip-",""),"-",".") = i2.internal_ip
			where i1.reported_by = 'datadog' and (i1.aws_hostname like '%10.0%' or i1.aws_hostname like '%10-0%') and i2.aws_hostname is not NULL
			group by i2.aws_hostname, i2.aws_region;
			"""
	data = sql(query)
	if csv:
		csv_out("ip_hostname_dupes.csv",data)
	return render_template('inventory.html',data=data)

def sql(query): # sql to view records, pass query
	conn = sqlite3.connect(db_filename) #write to local sqlite file
	cursor = conn.cursor()
	cursor.execute(query)
	data = cursor.fetchall()
	conn.close()
	return data

def csv_out(fname,data):
	with open("reports/"+fname,'wb') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		for row in data:
			csvwriter.writerow(row)

##########
###CODE###
##########

if __name__ == '__main__':
	db_filename = 'inv.db' #define db filename
	check_db(db_filename) # initize db
	app.run(host='0.0.0.0', port=5000, debug=True) #run web server


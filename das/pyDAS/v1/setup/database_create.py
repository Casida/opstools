#!/usr/bin/python

import MySQLdb

con = MySQLdb.Connect(user="root", passwd="abc123", db="das", host="localhost", port=3306)

db = con.cursor()

def drop_table(table_name):
    import warnings
    warnings.filterwarnings('ignore', "Unknown table.*")    

    drop_query = """DROP TABLE IF EXISTS %s;""" % table_name
    print "[-] Dropping table %s" % table_name
    db.execute(drop_query)
    con.commit()
    return

def create_table(table_name, params):
    
    print "[+] Creating table %s" % table_name
    db.execute(params)
    con.commit()
    return


device_create = """CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `das_station` int(11) DEFAULT NULL,
  `svcid` text,
  `dasid` text,
  `namespace_port` text,
  `dev_name` text,
  `dev_serial` text,
  `dev_purpose` text,
  `dev_size` bigint(20) DEFAULT NULL,
  `dev_used` bigint(20) DEFAULT NULL,
  `dev_sect_size` int(11) DEFAULT NULL,
  `dev_write_sec` bigint(20) DEFAULT NULL,
  `dev_read_sec` bigint(20) DEFAULT NULL,
  `date_created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `date_attached` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `date_detached` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `replication_started` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `replication_completed` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""

flags_create = """CREATE TABLE `flags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) DEFAULT NULL,
  `svcid` text,
  `date_created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `flag_active` int(11) DEFAULT '1',
  `flag_name` text,
  `flag_desc` text,
  `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""

jobs_create = """CREATE TABLE `jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `job_type` text,
  `machine_id` int(11) DEFAULT NULL,
  `job_id` int(11) DEFAULT NULL,
  `date_created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `job_started` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `job_completed` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `start_dev_write_sec` bigint(20) DEFAULT NULL,
  `end_dev_write_sec` bigint(20) DEFAULT NULL,
  `start_dev_read_sec` bigint(20) DEFAULT NULL,
  `end_dev_read_sec` bigint(20) DEFAULT NULL,
  `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `FK_jobs` (`device_id`),
  CONSTRAINT `FK_jobs` FOREIGN KEY (`device_id`) REFERENCES `device` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""

stations_create = """CREATE TABLE `stations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datacenter_id` int(11) DEFAULT NULL,
  `name` text,
  `addr` int(11) DEFAULT NULL,
  `usb_ports` int(11) DEFAULT NULL,
  `usb_hub` int(11) DEFAULT NULL,
  `usb_slots` int(11) DEFAULT NULL,
  `version` text,
  `kernel` text,
  `location` text,
  `date_created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `date_retired` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;"""

drop_table("jobs")
drop_table("device")
drop_table("flags")
drop_table("stations")

create_table("device", device_create)
create_table("flags", flags_create)
create_table("jobs", jobs_create)
create_table("stations", stations_create)

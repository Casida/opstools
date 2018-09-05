__author__ = 'snixon'
# Module for interacting with the DASdb

import MySQLdb
import config as cnf

# Database class and functions
class DasDB:

    def __init__(self, host=cnf.defDBHost, user=cnf.defDBUser, passwd=cnf.defDBPasswd, dbName=cnf.defDBname):
        self.db = MySQLdb.connect(host=host,
                                  user=user,
                                  passwd=passwd,
                                  db=dbName)
        self.cursor = self.db.cursor()

    def flag_add(self, service_id, name, description="None"):
        self.cursor.execute("""
            INSERT INTO flags
                (svcid, date_created, flag_name, flag_desc)
            VALUES
                (%s, %s, %s, %s)
                """, (service_id, dbToday, name, description)
        )
        self.db.commit()

    def flag_assign(self, flag_list, assign_id):
        format_strings = ','.join(['%s'] * len(flag_list))
        self.cursor.execute("""
            UPDATE flags
            SET device_id=%s
            WHERE id IN (%s) AND flag_active=1""" % (assign_id, format_strings),
                            tuple(flag_list)
        )
        self.db.commit()

    def flag_deactivate(self, flag_id):
        self.cursor.execute("""
            UPDATE flags
            SET flag_active=0
            WHERE id=%s
            """, (flag_id)
        )

    def flag_list(self, svcid):
        self.cursor.execute("""
            SELECT id from flags
            WHERE svcid=%s and flag_active=1;
            """, (svcid)
        )
        results = self.cursor.fetchall()
        flag_list = []
        if len(results) > 0:
            for i in results:
                flag_list.append(i[0])
        return flag_list

    def device_attach(self, serviceID, dasID, devName, devSerial, devPurpose, dateCreated=dbToday,
                      dateAttached=dbToday):
        stationID = self.find_das_stationID(defHostName)
        dev_base = get_dev_base(devName)
        devTotSize = get_dev_totsize(dev_base)
        devSectSize = get_dev_sectsize(dev_base)
        devReads, devWrites = get_dev_stats(dev_base)
        devReadSec = int(devReads) * devSectSize
        devWriteSec = int(devWrites) * devSectSize

        self.cursor.execute("""
            INSERT into device
                (das_station, svcid, dasid, dev_name, dev_serial, dev_purpose, dev_size,
                dev_sect_size, dev_write_sec, dev_read_sec, date_created, date_attached)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
            stationID, serviceID, dasID, devName, devSerial, devPurpose, devTotSize,
            devSectSize, devWriteSec, devReadSec, dateCreated, dateAttached)
        )
        self.db.commit()
        return self.cursor.lastrowid

    def device_detach(self, serviceID, dateDetached=dbToday):
        stationID = self.find_das_stationID()
        instID = get_pid(serviceID)
        self.cursor.execute("""
            UPDATE device
                SET date_detached=%s
            WHERE id=%s and das_station=%s and svcid=%s and date_detached=0;
            """, (dateDetached, instID, stationID, serviceID)
        )
        self.db.commit()

    def find_das_stationID(self, hostname=defHostName):
        self.cursor.execute("""
            SELECT id from stations where name=%s and date_retired=0;
            """, (hostname)
        )
        results = self.cursor.fetchone()
        if len(results) > 0:
            stationID = results[0]
        else:
            stationID = 0
        return stationID

    def station_add(self, addr, usbPorts, usbHub, usbSlots, location, stationName=defHostName):
        ipAddr = pack_ip(addr)
        version = cnf.version
        kernel = os.uname()[2]
        self.cursor.execute("""
            INSERT INTO stations
                (name, addr, usb_ports, usb_hub, usb_slots, version, kernel, location, date_created)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (stationName, ipAddr, usbPorts, usbHub, usbSlots, version, kernel, location, dbToday)
        )
        self.db.commit()
        return self.cursor.lastrowid

    def seed_jobs(self, serviceID):
        instID = get_pid(serviceID)
        for jobType, machine, job in get_jobs(serviceID):
            self.cursor.execute("""
                INSERT into jobs
                    (device_id, job_type, machine_id, job_id, date_created)
                VALUES
                    (%s, %s, %s, %s, %s);
                """, (instID, jobType, machine, job, dbToday)
            )
        self.db.commit()

    def start_dev_replication(self, serviceID, namespacePort, dateStarted=dbToday):
        usedBytes = get_dev_used_size(serviceID)
        instID = get_pid(serviceID)
        stationID = self.find_das_stationID()
        self.cursor.execute("""
            UPDATE device
                SET replication_started=%s, namespace_port=%s, dev_used=%s
            WHERE id=%s and das_station=%s and svcid=%s;
            """, (dateStarted, namespacePort, usedBytes, instID, stationID, serviceID)
        )
        self.db.commit()

    def stop_dev_replication(self, serviceID, dateStopped=dbToday):
        instID = get_pid(serviceID)
        stationID = self.find_das_stationID()
        self.cursor.execute("""
            UPDATE device
                SET replication_completed=%s
            WHERE id=%s and das_station=%s and svcid=%s;
            """, (dateStopped, instID, stationID, serviceID)
        )
        self.db.commit()

    def get_job_id(self, job):
        tempSplit = str(job).split('/')
        id_list = []
        if len(tempSplit) == 1:
            job_type = tempSplit[0]
            machine = "1"
            job = "1"
        elif len(tempSplit) == 2:
            job_type = "FILE"
            machine = tempSplit[0]
            job = tempSplit[1]
        else:
            job_type = tempSplit[0]
            machine = tempSplit[1]
            job = tempSplit[2]
        self.cursor.execute("""
            SELECT id from jobs WHERE
                jobs.job_type = %s
            AND
                jobs.machine_id = %s
            AND
                jobs.job_id = %s;
            """, (job_type, machine, job)
        )
        results = self.cursor.fetchall()
        for i in results:
            id_list.append(i[0])
        return id_list

    def get_dev_name(self, serviceID):
        instID = get_pid(serviceID)
        self.cursor.execute("""
            SELECT dev_name from device
            WHERE id=%s;
            """, (instID)
        )
        results = self.cursor.fetchone()[0]
        if len(results) > 0:
            dev_name = results
        else:
            dev_name = 0
        return dev_name


    def job_start_replication(self, idList, serviceID):
        devName = get_dev_base(self.get_dev_name(serviceID))
        devSectSize = get_dev_sectsize(devName)
        devReads, devWrites = get_dev_stats(devName)
        devReadSec = int(devReads) * devSectSize
        devWriteSec = int(devWrites) * devSectSize
        for job in idList:
            self.cursor.execute("""
                UPDATE jobs
                    SET job_started=%s, start_dev_read_sec=%s, start_dev_write_sec=%s
                WHERE id=%s;
            """, (dbToday, devReadSec, devWriteSec, job)
            )
        self.db.commit()

    def job_stop_replication(self, idList, serviceID):
        devName = get_dev_base(self.get_dev_name(serviceID))
        devSectSize = get_dev_sectsize(devName)
        devReads, devWrites = get_dev_stats(devName)
        devReadSec = int(devReads) * devSectSize
        devWriteSec = int(devWrites) * devSectSize
        for job in idList:
            self.cursor.execute("""
                UPDATE jobs
                    SET job_completed=%s, end_dev_read_sec=%s, end_dev_write_sec=%s
                WHERE id=%s;
            """, (dbToday, devReadSec, devWriteSec, job)
            )
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()
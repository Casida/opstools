__author__ = 'snixon'
# Library of DAS utility functions
import os
import glob
import struct
import socket
import signal
import datetime
import config as cnf

today = datetime.datetime.now()
dbToday = today.strftime("%Y-%m-%d %H:%M:%S")

# DB PIDs
def set_pid(svcid, rowid, cache_dir=cnf.cacheDIR):
    cache_path = "%s/%s" % (cache_dir, svcid)
    inst_id = open(cache_path, 'w+')
    inst_id.write(str(rowid))
    inst_id.close()
    return


def get_pid(svcid, cache_dir=cnf.cacheDIR):
    cache_path = "%s/%s" % (cache_dir, svcid)
    if os.path.isfile(cache_path):
        f = open(cache_path, 'r')
        pid = f.read()
        f.close()
    else:
        pid = 0
    return pid


def clear_pid(serviceID, CACHE_DIR=cacheDIR):
    cache_path = "%s/%s" % (CACHE_DIR, serviceID)
    if os.path.isfile(cache_path):
        os.remove(cache_path)
        pid = 0
    else:
        pid = 1
    return pid


# Device Functions
def get_dev_base(dev_name):
    return dev_name.split('/')[2]


def build_das_dict():
    import glob

    id_path = glob.glob('/dev/ax/das*')
    svcid_path = glob.glob('/dev/ax/.dasids/*')
    id_dict = {}
    das_dict = {}
    for i in id_path:
        id = i.split('/')[3]
        dev = os.readlink(i)
        id_dict[id] = dev

    for i in svcid_path:
        id = i.split('/')[4]
        svcid = os.readlink(i)
        das_dict[svcid] = {'dev': id_dict[id], 'dasid': id}
    return das_dict


def get_dev_totsize(dev):
    # Using /sys filesystem so we don't need to be root to get block sizes
    # /sys/block/sda/sda2/size contains the partition size in 512k blocks
    dev_path = '/sys/block/%s/%s2/size' % (dev, dev)
    f = open(dev_path, 'ro')
    dev_size = f.read()
    f.close()
    return int(dev_size) * 512


def get_dev_sectsize(dev):
    dev_path = '/sys/block/%s/queue/hw_sector_size' % dev
    f = open(dev_path, 'ro')
    sect_size = f.read()
    f.close()
    return int(sect_size)


def get_dev_stats(dev):
    dev_path = '/sys/block/%s/%s2/stat' % (dev, dev)
    f = open(dev_path, 'ro')
    dev_stats = ' '.join(f.read().split()).split()
    f.close()
    dev_reads = dev_stats[2]
    dev_writes = dev_stats[6]
    return dev_reads, dev_writes


def get_dev_used_size(serviceid):
    mount_path = '/uptiva/mounts/%s/offsite' % serviceid
    stat = os.statvfs(mount_path)
    return (stat.f_blocks - stat.f_bfree) * stat.f_frsize


# Network functions
def pack_ip(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def unpack_ip(packed_addr):
    return socket.inet_ntoa(struct.pack("!I", packed_addr))


# Jobs Functions

def get_jobs(svcid):

    jobList = []
    files_path = '/uptiva/mounts/%s/offsite/[0-9]*/[0-9]*' % svcid
    ebr_path = '/uptiva/mounts/%s/offsite/EBR*' % svcid
    sva_path = '/uptiva/mounts/%s/offsite/SVA/[0-9]*/[0-9]*' % svcid
    fileDepth3 = glob.glob(files_path)
    ebrDepth3 = glob.glob(ebr_path)
    svaDepth3 = glob.glob(sva_path)
    dirsDepth3 = []
    for path in fileDepth3, ebrDepth3, svaDepth3:
        dirsDepth3.append(filter(lambda f: os.path.isdir(f), path))
    for pathname in [item for sublist in dirsDepth3 for item in sublist]:
        tempSplit = str(pathname).split('/')
        tempList = []
        if len(tempSplit) == 6:
            tempList.append(tempSplit[5])
            tempList.append("1")
            tempList.append("1")
        elif len(tempSplit) == 7:
            tempList.append("FILE")
            tempList.append(tempSplit[5])
            tempList.append(tempSplit[6])
        else:
            tempList.append(tempSplit[5])
            tempList.append(tempSplit[6])
            tempList.append(tempSplit[7])
        jobList.append(tempList)
    return jobList

class action:

    def __init__(self):
        self.log = cnf.log(__name__).logger

    def get_rep_pid(self, svcid, pid_dir=cnf.pidDIR):
        pid_path = "%s/%s/replicate-*.pid" % (pid_dir, svcid)
        globbed_path = glob.glob(pid_path)
        if os.path.isfile(globbed_path[0]):
            f = open(globbed_path[0], 'r')
            pid = f.read()
            f.close()
        else:
            pid = 0
        return pid

    def stop_das_replication(self, svcid):
        self.log.info('Stopping das: %s', svcid)
        self.running_pid = get_rep_pid(svcid)
        self.process_group = os.getpgid(self.running_pid)
        self.log.info('Killing PG: %s, based on process: %s', (self.process_group, self.running_pid))
        os.killpg(self.process_group, signal.TERM)
        clear_pid(svcid)
        return


    def stop_das_update(self, svcid):
        return



















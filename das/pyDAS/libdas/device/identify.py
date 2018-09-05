__author__ = 'snixon'

import os
import re
import hashlib
from glob import glob
from libdas import log
from libdas import config
from libdas import utility

class Identify:

    def __init__(self):
        self.log = log.log(__name__).logger

    def offset(self, device, skip_bytes, read_bytes):
        offset_lengths = [512, 524288]
        for offset in offset_lengths:
            skip = offset + skip_bytes
            f = open(device, 'rb')
            f.seek(skip)
            result = f.read(read_bytes)
            f.close()
            self.log.info('Found key: %s at offset: %s' % (re.sub(r'[^\w]', '', result), offset))
        return result


    def drive_info(self, path):
        # Expects paths from /proc/scsi/usb-storage/dev_files or similar
        if os.path.isfile(path):
            try:
                fd = open(path, 'rb')
                desc = fd.readlines()
                fd.close()
            except IOError:
                self.log.warning("Couldn't open %s" % path)
                return False
            drive_dict = {}
            for i in desc:
                item = i.strip().split(': ')
                try:
                    drive_dict.update({item[0].lower(): item[1]})
                except IndexError:
                    drive_dict.update({item[0].lower(): ''})
            return drive_dict
        else:
            return False


    def keygen(self, dev_serial, type='AxcientDirectAttachedStorage'):
        m = hashlib.md5()
        m.update(type)
        m.update(dev_serial)
        result = m.hexdigest()
        self.log.info('Type: %s, Serial: %s, Key: %s', (type, dev_serial, result))
        return result


    def magic(self, device):
        # Returns {'dev': device, 'svcid': 'ABCD', 'parts': '2'}
        self.log.info('Magic invoked....here goes nothing')
        safe_word = 'deadbeef'
        read_key = self.offset(device, 32, 32)
        self.log.info('Read key: %s from device' % read_key)
        # Generate some paths
        scsi_path = '/sys/block/%s/device/scsi_disk:*' % device.split('/')[-1]
        dev_path = glob(scsi_path)[0]
        id = dev_path.split('/')[-1].split(':')[1]
        usb_path = '/proc/scsi/usb-storage/%s' % id
        gen_key = self.keygen(self.drive_info(usb_path)['serial number'])
        self.log.info('Generated key: %s from device' % gen_key)
        results = {}
        results.update({'dev': device})
        if (read_key == gen_key):
            self.log.info("Matched device key")
            results.update({'parts': self.offset(device, 96, 4096).split('=')[0]})
            id_string = self.offset(device, 8288, 1024)
            if (id_string[0:8] == safe_word):
                results.update({'svcid': id_string[8:12]})
            elif (id_string[6:14] == safe_word):
                results.update({'svcid': id_string[14:18]})
            else:
                results.update({'svcid': 'NOTFOUND'})
        return results

class Links:

    def __init__(self):
        self.log = log.log(__name__).logger

    def das_id_gen(self, basepath=config.basePath):
        daspath = os.path.join(basepath, 'das*')
        das_list = glob(daspath)
        try:
            cur = max(das_list)
        except ValueError, e:
            new_das = 'das0'
            return new_das
        self.log.debug('Currently %s DASes on station', len(das_list))
        self.log.debug('Identified %s as highest order das device', cur)
        new_das = 'das' + str(int(cur.split('das')[1]) + 1)
        self.log.debug('Next das device is: %s', new_das)
        return new_das

    def das_linker(self, das_dict, basepath=config.basePath):
        cur_links = utility.link_info()
        svcid = das_dict['svcid']
        if not cur_links.has_key(svcid):
            # Get the next DAS ID
            next_das = self.das_id_gen()
            das_dict.update({'dasid': next_das})
            next_das_path = os.path.join(basepath, next_das)
            next_dasid_path = os.path.join(basepath, '.dasids', next_das)
            das_dev = das_dict['dev'] + das_dict['parts']
            # Build outer links
            try:
                os.symlink(das_dev, next_das_path)
                self.log.info('Successfully created link: %s -> %s', (next_das_path, das_dev))
            except OSError, e:
                self.log.warning('Failed to create link %s -> %s: %s', (next_das_path, das_dev, e.strerror))
                return False
            # Build inner links
            try:
                os.symlink(svcid, next_dasid_path)
                self.log.info('Successfully created dasid link: %s -> %s', (next_dasid_path, svcid))
            except OSError, e:
                self.log.warning('Failed to create dasid link %s -> %s: %s', (next_dasid_path, svcid, e.strerror))
                return False
            return das_dict
        else:
            self.log.info('Link already exists for %s -> %s')
            das_dict.update({'dasid': cur_links['svcid']['dasid']})
            return das_dict

    def das_unlinker(self, svcid, basepath=config.basePath):
        dasid_path = os.path.join(basepath, '.dasids', 'das*')
        cur_das = glob(dasid_path)
        for das in cur_das:
            try:
                if os.readlink(das) == svcid:
                    self.log.info('Found matching DAS: %s' % das)
                    dasid = das.split('/')[-1]
                    os.unlink(das)
                    self.log.info('Unlinked %s' % das)
                    daspath = os.path.join(basepath, dasid)
                    os.unlink(daspath)
                    self.log.info('Unlinked %s' % daspath)
            except OSError, e:
                self.log.warning("Couldn't read link %s: %s" % (das, e.strerror))
                return False
        return True


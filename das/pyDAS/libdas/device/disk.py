__author__ = 'snixon'

import os
import subprocess
from libdas import config
from libdas import utility

class Mount:

    def __init__(self):
        self.log = log.log(__name__).logger

    def attach_das(self, das_dict):
        # mount /dev/ax/dasN /uptiva/volumes/svcid
        # This mounts or 'attaches' the physical volume, to do anything useful we still have to decrypt the volume
        volpath = os.path.join('/uptiva/volumes', das_dict['svcid'])
        devpath = os.path.join(config.basePath, das_dict['dasid'])
        if utility.check_perm(volpath)['type'] == 'DIR' and utility.check_perm(devpath)['type'] == 'LINK':
            self.log.info('Paths exist, attempting mount %s -> %s' % (devpath, volpath))
            p = subprocess.Popen(['/usr/bin/mount', '-t', 'xfs', devpath, volpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            mnt_data, mnt_err = p.communicate()
            if mnt_err:
                self.log.warning('Mount failure: %s' % mnt_err)
                return False
            else:
                self.log.info('Mount succeeded: mounted %s -> %s' % (devpath, volpath))
                return True

    def detach_das(self, svcid):
        link_dict = utility.link_info()
        if link_dict.has_key(svcid):
            device = link_dict[svcid]['dev']
            p = subprocess.Popen(['/usr/bin/umount', device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            umnt_data, umnt_err = p.communicate()
            if umnt_err:
                self.log.warning('Error un-mounting device %s: %s' % (device, umnt_err))
                return False
            else:
                self.log.info('Successfully detached device: %s' % device)
                return True
        else:
            self.log.warning('SVCID %s not found in links' % svcid)
            return False


class EncFS:

    def __init__(self):
        self.log = log.log(__name__).logger

    # We can have "future" other methods to get private keys here
    def openssl_get_key(self, svcid, privkey=config.privKey):
        key_path = os.path.join('/uptiva/volumes', svcid, '.ax')
        key_path_perms = utility.check_perm(key_path)
        if key_path_perms and key_path_perms['type'] == 'FILE':
            self.log.info('Found keyfile at: %s' % key_path)
            p = subprocess.Popen(['/usr/bin/openssl', 'rsautl', '-decrypt', '-inkey', privkey, '-in', key_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            key_data, key_err = p.communicate()
            if key_err:
                self.log.warning('Error decrypting key: %s' % key_err)
                return False
            elif key_data:
                self.log.info('Decrypted key %s, using OpenSSL Method' % key_path)
                return key_data
            else:
                self.log.warning('OpenSSL returned no results')
                return False
        else:
            self.log.wanring('Error reading key_file %s' % key_path)
            return False

    def mount_encfs_volume(self, svcid):
        encfs_key = self.openssl_get_key(svcid)
        vol_path = os.path.join('/uptiva/volumes', svcid)
        mnt_path = os.path.join('/uptiva/mounts', svcid, 'offsite')
        vol_perms = utility.check_perm(vol_path, 'DIR')
        mnt_perms = utility.check_perm(mnt_path, 'DIR')
        if encfs_key:
            if vol_perms:
                if mnt_perms:
                    # We do this because subprocess.stdin can't write to the prompt thrown by encfs -- don't judge me!
                    extpass = '--extpass=echo %s' % encfs_key
                    p = subprocess.Popen(['/usr/bin/encfs', extpass, vol_path, mnt_path, '--', '-o', 'allow_root'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    mnt_data, mnt_err = p.communicate()
                    if mnt_err:
                        self.log.warning('Error mounting EncFS volume: %s' % mnt_err)
                        return False
                    else:
                        self.log.info('Successfully mounted EncFS volume: %s -> %s' % (vol_path, mnt_path))
                        return True
                else:
                    self.log.warning('Mount path error: %s: check existence and permissions' % mnt_path)
                    return False
            else:
                self.log.warning('Volume path error: %s: check existence and permissions' % vol_path)
                return False
        else:
            self.log.warning("Couldn't retrieve EncFS key")
            return False

    def umount_encfs_volume(self, svcid):
        mnt_path = os.path.join('/uptiva/mounts', svcid, 'offsite')
        mnt_perms = utility.check_perm(mnt_path, 'DIR')
        if mnt_perms:
            p = subprocess.Popen(['/usr/bin/fusermount', '-u', mnt_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            umnt_data, umnt_err = p.communicate()
            if umnt_err:
                self.log.warning('Error unmounting %s: %s' % (mnt_path, umnt_err))
                return False
            else:
                self.log.info('Successfully unmounted %s' % mnt_path)
                return True
        else:
            self.log.warning('Path not found: %s' % mnt_path)
            return False

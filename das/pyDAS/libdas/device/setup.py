__author__ = 'snixon'
# Module to setup DASes for initial seeding
import os
import pwd
import subprocess
from libdas import log
from libdas import utility


class User:

    def __init__(self):
        self.log = log.log(__name__).logger

    def user_create(self, user):
        user_home = '/home/%s' % user
        try:
            pwd.getpwnam(user)
        except KeyError:
            p = subprocess.Popen(['/usr/sbin/useradd', '-d', user_home, '-m', '-G', 'fuse', user], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            user_data, user_err = p.communicate()
            if user_err:
                self.log.warning('Error during create process: %s' % user_err)
                return False
        else:
            return True

    def user_dir_build(self, user):
        vol_path = '/uptiva/volumes/%s' % user
        mnt_path = '/uptiva/mounts/%s/offsite' % user
        ssh_path = '/home/%s/.ssh' % user
        uid, gid = utility.get_user_ids(user).values()
        if not os.path.exists(vol_path):
            try:
                os.makedirs(vol_path)
                self.log.debug('Created volume path: %s' % vol_path)
            except OSError, e:
                self.log.warning('Failed to create volume path: %s' % e.strerror)
                return False
        else:
            self.log.info('Failed to create volume path: %s: File Exists' % vol_path)
            return False
        if not os.path.exists(mnt_path):
            try:
                os.makedirs(mnt_path)
                self.log.debug('Created mount path: %s' % mnt_path)
            except OSError, e:
                self.log.warning('Failed to create mount path: %s' % e.strerror)
                return False
        else:
            self.log.info('Failed to create mount path: %s: File Exists' % mnt_path)
            return False
        if not os.path.exists(ssh_path):
            try:
                os.makedirs(ssh_path, mode=0700)
                self.log.debug('Created ssh path: %s' % ssh_path)
            except OSError, e:
                self.log.warning('Failed to create ssh path: %s' % e.strerror)
                return False
        else:
            self.log.info('Failed to create ssh path: %s: File Exists' % ssh_path)
            return False
        # Chown newly created dirs
        try:
            os.chown(vol_path, uid, gid)
            self.log.debug('Chowned %s', vol_path)
        except OSError, e:
            self.log.warning('Failed to chown %s: %s' % (vol_path, e.strerror))
            return False
        try:
            os.chown(mnt_path, uid, gid)
            self.log.debug('Chowned %s', mnt_path)
        except OSError, e:
            self.log.warning('Failed to chown %s: %s' % (mnt_path, e.strerror))
            return False
        try:
            os.chown(ssh_path, uid, gid)
            self.log.debug('Chowned %s', ssh_path)
        except OSError, e:
            self.log.warning('Failed to chown %s: %s' % (ssh_path, e.strerror))
            return False
        return True


    def ssh_keygen(self, user):
        uid, gid = utility.get_user_ids(user).values()
        ssh_path = '/home/%s/.ssh' % user
        ssh_key = os.path.join(ssh_path, 'id_rsa')
        if utility.check_perm(ssh_path)['type'] == 'DIR':
            self.log.debug('User .ssh path exists: %s, generating key' % ssh_path)
            p = subprocess.Popen(['/usr/bin/ssh-keygen', '-q', '-t', 'rsa', '-f', ssh_key, '-N', '', '-C', user], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            user_data, user_err = p.communicate()
            if user_err:
                self.log.warning('Error creating ssh keypair: %s' % user_err)
                return False
            else:
                self.log.info('Created ssh-keypair: %s' % ssh_key)
                pub_key_file = ssh_key + '.pub'
                os.chown(ssh_key, uid, gid)
                os.chown(pub_key_file, uid, gid)
                return ssh_key
        else:
            self.log.warning('User .ssh path does not exist: %s' % ssh_path)
            return False
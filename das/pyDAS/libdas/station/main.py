__author__ = 'snixon'

import os
from libdas import log, utility, config

class BaseChecks:

    def __init__(self):
        self.log = log.log(__name__).logger

    def check_paths(self, dasbasepath=config.dasBasePath):
        devpath = utility.check_perm(dasbasepath)
        if devpath['perms'] and devpath['type'] == 'DIR':
            self.log.info('%s passes perm checks', dasbasepath)
            dasidpath = os.path.join(dasbasepath, '.dasids')
            idpath = utility.check_perm(dasidpath)
            if idpath['perms'] and idpath['type'] == 'DIR':
                self.log.info('%s passes perm checks', dasidpath)
                return True
            else:
                self.log.warning('%s issue: Type: %s, Perms: %s', (dasidpath, idpath['type'], idpath['perms']))
        else:
            self.log.warning('%s issue: Type: %s, Perms: %s', (config.dasBasePath, devpath['type'], devpath['perms']))
        return False
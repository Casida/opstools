__author__ = 'snixon'

import logging
import config as cnf

class log:

    def __init__(self, name, logfile=cnf.deflogFile, logformat=cnf.deflogFormat, level=cnf.deflogLevel):
        self.logger = logging.getLogger(name)
        self.logLevel = {'DEBUG': logging.DEBUG,
                         'INFO': logging.INFO,
                         'WARNING': logging.WARNING,
                         'ERROR': logging.ERROR,
                         'CRITICAL': logging.CRITICAL}
        logging.basicConfig(format=logformat, level=self.logLevel[level])
        self.logger.debug('TEST')

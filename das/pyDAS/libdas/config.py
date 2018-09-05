__author__ = 'snixon'

# Database Setup
defDBHost = 'hostname'
defDBUser = 'user'
defDBPasswd = 'pass'
defDBname = 'db_name'

# General Setup
dateFMT = '%Y-%m-%d %H:%M:%S'
cacheDIR = '/var/cache/das'
pidDIR = '/var/run/axcient/das'
basePath = '/dev/ax'
version = '0.2'

# EncFS Setup
privKey = '/etc/encfs/private.pem'

# Logging setup
deflogFile = '/var/log/das.log'
deflogFormat = '%(asctime)s: [%(module)s] [%(name)s] [%(funcName)s] %(message)s'
deflogLevel = 'DEBUG'
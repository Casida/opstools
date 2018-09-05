__author__ = 'snixon'

import os
import pwd
import grp
from glob import glob
from libdas import config


def check_perm(path, type=False):
    check_dict = {}
    if os.path.isdir(path):
        check_dict.update({'perms': os.access(path, os.R_OK or os.W_OK or os.X_OK)})
        check_dict.update({'type': 'DIR'})
        if type == 'DIR':
            ret = True
        else:
            ret = False
    elif os.path.isfile(path):
        check_dict.update({'perms': os.access(path, os.R_OK or os.W_OK or os.X_OK)})
        check_dict.update({'type': 'FILE'})
        if type == 'FILE':
            ret = True
        else:
            ret = False
    elif os.path.islink(path):
        check_dict.update({'perms': os.access(path, os.R_OK or os.W_OK or os.X_OK)})
        check_dict.update({'type': 'LINK'})
        if type == 'LINK':
            ret = True
        else:
            ret = False
    else:
        check_dict = False
        ret = False
    if type:
        return ret
    else:
        return check_dict


def get_user_ids(user):
    user_dict = {}
    try:
        uid = pwd.getpwnam(user)[2]
        gid = grp.getgrgid(uid)[2]
        user_dict.update({'uid': uid})
        user_dict.update({'gid': gid})
    except KeyError:
        return False
    return user_dict


def link_info(basepath=config.basePath):
    das_path = os.path.join(basepath, 'das*')
    cur_das = glob(das_path)
    das_link_dict = {}
    for dasid in cur_das:
        dasid_path = os.path.join(basepath, '.dasids', dasid.split('/')[-1])
        temp = {}
        temp.update({'dasid': dasid.split('/')[-1]})
        temp.update({'dev': os.readlink(dasid)})
        das_link_dict.update({os.readlink(dasid_path): temp})
    return das_link_dict
# -*- coding: utf-8 -*-
import hashlib
import time
from app import load_app_config


def get_user_info_hash(user_name, password):
    md5_secrethash = hashlib.md5()
    md5_secrethash.update(password + user_name)
    secrect_hash = md5_secrethash.hexdigest()

    md5_userhash = hashlib.md5()
    md5_userhash.update(load_app_config().SALT_STRING + user_name)
    user_hash = md5_userhash.hexdigest()

    return secrect_hash, user_hash


def gen_session_id_for_user(user_name):
    return hashlib.sha256("{}:{}".format(
        str(time.time()),
        user_name
    )).hexdigest()


def is_admin(user_id):
    return user_id == 1


if __name__ == "__main__":
    import sys
    print get_user_info_hash(sys.argv[1], sys.argv[2])


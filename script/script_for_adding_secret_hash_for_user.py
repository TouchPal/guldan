# -*- coding: utf-8 -*-

import hashlib
import pymysql

GULDAN_DB_CONN_STR = 'mysql://root:root@127.0.0.1:3306/guldandb?charset=utf8mb4'
SALT_STRING = "test"

USER_HASH = {}

def generate_user_hash(user_name, salt_string):
    md5_userhash = hashlib.md5()
    md5_userhash.update(SALT_STRING + user_name)
    return md5_userhash.hexdigest()


def patch_for_user_table(cursor):
    cursor.execute("select id,name from user")
    data = cursor.fetchall()
    for u in data:
        new_user_hash = generate_user_hash(u[1], SALT_STRING)
        cmd = "update user set user_hash=\"{}\" where id={}".format(new_user_hash, u[0])
        print cmd
        cursor.execute(cmd)
        USER_HASH[u[0]] = new_user_hash

def patch_for_privilege(cursor):
    for user_id, user_hash in USER_HASH.items():
        cmd = "update privilege set user_hash=\"{}\" where user_id={}".format(USER_HASH[user_id], user_id)
        print cmd
        cursor.execute(cmd)


def pack_for_user_hash():
    db = pymysql.connect(host="127.0.0.1", user="root", password="root", db="guldandb", charset="utf8mb4")
    try:
        with db.cursor() as cursor:
            patch_for_user_table(cursor)
            patch_for_privilege(cursor)
    finally:
        db.commit()
        db.close()


if __name__ == "__main__":
    pack_for_user_hash()


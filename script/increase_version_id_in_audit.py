#!/usr/bin/env python
import collections
import pymysql
import json

db_conn = pymysql.connect(
    host="127.0.0.1",
    port=3500,
    user="root",
    password="root",
    db="guldandb",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)


def get_id_dict(resource_type):
    sql_template = u"select id, resource_id, resource_type, updated_at from audit where resource_type={resource_type} and action in (0, 1) order by created_at"
    sql = sql_template.format(resource_type=resource_type)
    with db_conn.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

        result_dict = collections.defaultdict(list)
        for r in result:
            result_dict["{}_{}".format(r["resource_id"], r["resource_type"])].append(r["id"])

    return result_dict


def increase_version_number(result_dict):
    select_template = "select updated_at from audit where id={id}"
    sql_template = "update audit set version_id={version}, updated_at=\'{updated_at}\' where id={id}"
    for k, v in result_dict.items():
        with db_conn.cursor() as cursor:
            version = 1
            for i in v:
                select = select_template.format(id=i)
                cursor.execute(select)
                updated_at = str(cursor.fetchall()[0]["updated_at"])
                sql = sql_template.format(version=version, id=i, updated_at=updated_at)
                version += 1
                print sql
                cursor.execute(sql)


def run(resource_type):
    result_dict = get_id_dict(resource_type)
    increase_version_number(result_dict)


if __name__ == "__main__":
    try:
        run(1)
        run(2)
        run(3)
        db_conn.commit()
    except:
        db_conn.rollback()
        raise
    finally:
        db_conn.close()


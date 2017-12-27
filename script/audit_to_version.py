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


def get_resource_id(resource_type):
    with db_conn.cursor() as cursor:
        sql_template = "select resource_id, resource_type from audit where is_deleted=0 and resource_type={resource_type}"
        sql = sql_template.format(resource_type=resource_type)
        cursor.execute(sql)
        result = cursor.fetchall()
        result_set = set()
        
        for one in result:
            result_set.add(one["resource_id"])

        return result_set


def get_audits_for_modification(resource_type, resource_ids):
    with db_conn.cursor() as cursor:
        sql_template = "select resource_id, resource_last_value, resource_new_value, created_at from audit where action=1 and resource_type={resource_type} and resource_id in ({resource_ids}) order by created_at"
        sql = sql_template.format(resource_type=resource_type, resource_ids=",".join(str(i) for i in resource_ids))
        cursor.execute(sql)

        result = cursor.fetchall()

        result_dict = collections.defaultdict(list)
        for record in result:
            result_dict[record["resource_id"]].append(record)

        return result_dict


def write_first_version(resource_id, resource_type, audit, sql_template):
    if resource_type == 3:
        resource_content = json.loads(audit["resource_last_value"], encoding="utf-8")["item_data"]
    else:
        resource_content = ""

    sql = sql_template.format(
        resource_id=resource_id,
        resource_type=resource_type,
        version_id=1,
        resource_content=resource_content,
        resource_visibility=int(json.loads(audit["resource_last_value"])["visibility"]),
        is_deleted=0,
        updated_at=audit["created_at"],
        created_at=audit["created_at"]
    )
    print sql

    with db_conn.cursor() as cursor:
        cursor.execute(sql)


def write_for_one_resource(resource_id, resource_type, audit_records, sql_template):
    write_first_version(resource_id, resource_type, audit_records[0], sql_template)
    version = 2
    with db_conn.cursor() as cursor:
        for record in audit_records:
            if resource_type == 3:
                resource_content = json.loads(record["resource_new_value"], encoding="utf-8")["item_data"]
            else:
                resource_content = ""

            sql = sql_template.format(
                resource_id=resource_id,
                resource_type=resource_type,
                version_id=version,
                resource_content=resource_content,
                resource_visibility=int(json.loads(record["resource_new_value"])["visibility"]),
                is_deleted=0,
                updated_at=record["created_at"],
                created_at=record["created_at"]
            )
            print sql
            version += 1
            cursor.execute(sql)
    
    return version - 1


def update_resource_current_version_id(resource_id, resource_type, version_id):
    select_template = "select updated_at from {resource} where id={resource_id}"
    sql_template = "update {resource} set current_version_id={version_id},updated_at=\'{updated_at}\' where id = {resource_id}"
    if resource_type == 3:
        resource = "item"
    elif resource_type == 2:
        resource = "project"
    elif resource_type == 1:
        resource = "org"
    else:
        resource = ""

    select = select_template.format(resource=resource, resource_id=resource_id)
    with db_conn.cursor() as cursor:
        cursor.execute(select)
        updated_at = str(cursor.fetchall()[0]["updated_at"])

        sql = sql_template.format(resource=resource, version_id=version_id, resource_id=resource_id, updated_at=updated_at)
        print sql
        cursor.execute(sql)


def write_to_version(resource_type, audit_dict):
    sql_template = u"insert into version (resource_id, resource_type, version_id, resource_content, resource_visibility, is_deleted, updated_at, created_at) values ({resource_id}, {resource_type}, {version_id}, \'{resource_content}\', {resource_visibility}, {is_deleted}, \'{updated_at}\', \'{created_at}\')"
    for resource_id, audit_records in audit_dict.items():
        version_id = write_for_one_resource(resource_id, resource_type, audit_records, sql_template)
        update_resource_current_version_id(resource_id, resource_type, version_id)


def run(resource_type):
    resource_ids = get_resource_id(resource_type)
    modify_audits_dict = get_audits_for_modification(resource_type, resource_ids)
    write_to_version(resource_type, modify_audits_dict)


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

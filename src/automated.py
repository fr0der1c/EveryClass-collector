import time
import os
import json
import mysql.connector
import settings
from predefined import get_semester_code_for_db
from retrieve import retrieve
from verify_semester import verify
from stu_data_json_compare import compare_json
from process_data import process

"""
This is automated script for updating information.
1. Save raw student data information to stu_data_raw.txt
2. Change old_json_file in settings
3. Run this script
"""


def fix_json(old_json_filename):
    """
    1. Detect content in stu_data_raw.txt and save it to a json file.
    2. Compare two json file and tell the difference
    3. Change json filename in settings

    :return: none
    """
    text = ""
    new_json_filename = "stu_data_%s.json" % time.strftime('%Y%m%d', time.localtime(time.time()))
    with open("stu_data_raw.txt") as raw_file, \
            open(new_json_filename, "w") as json_file:
        text = str(raw_file.read()).replace("'", '"')
        text = text.replace('xm', '"xm"')
        text = text.replace('xs0101id', '"xs0101id"')
        text = text.replace('xh', '"xh"')

        json_file.write(text)
    compare_json(old=old_json_filename, new=new_json_filename)

    with open("stu_data_version.json") as f:
        f.write(json.dumps({"stu_data_json_name": new_json_filename}))


def clean_directory():
    """
    Clean raw_data directory

    :return: none
    """
    for each in os.listdir(os.path.join(os.getcwd(), 'raw_data')):
        os.remove(each)
    retrieve()


def clean_database():
    """
    Clean ec_students_[semester] and ec_classes_[semester] table

    :return: none
    """
    conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
    cursor = conn.cursor()

    query = "TRUNCATE ec_students_%s" % get_semester_code_for_db(settings.SEMESTER)
    cursor.execute(query)
    query = "TRUNCATE ec_classes_%s" % get_semester_code_for_db(settings.SEMESTER)
    cursor.execute(query)
    cursor.close()
    conn.close()


if __name__ == "__main__":
    with open("stu_data_version.json") as f:
        old_json_file = json.load(f)["stu_data_json_name"]

    fix_json(old_json_file)
    clean_directory()
    retrieve()
    clean_database()
    process()
    verify()

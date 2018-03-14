"""
用于调整数据表结构的升级脚本
需要对每个学期运行一次
目的是把姓名和xs0101id导入ec_available_semesters
"""
import mysql.connector
import json
import settings
from termcolor import cprint

names_json = open("stu_data.json")
#
names = json.load(names_json)
conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
'''
Above are settings you should notice before running this programme.
'''
cursor = conn.cursor()
count = 0
DEBUG = settings.DEBUG
for each_student in names:
    if DEBUG:
        print('Processing student: [%s]%s' % (each_student['xh'], each_student['xm']))
    query = "UPDATE ec_available_semesters SET xs0101id=%s, name=%s WHERE xh=%s"
    cursor.execute(query, (each_student['xs0101id'], each_student['xm'], each_student['xh']))
    count = count + 1
    if count % 100 == 0:
        cprint('Finished %s entries.' % count, color='blue', attrs=["bold"])
conn.commit()
cursor.close()
conn.close()
cprint("Finished!(Total %s)" % count, color='blue', attrs=["bold"])

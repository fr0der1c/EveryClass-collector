import mysql.connector
import json
import settings
from termcolor import cprint

names_json = open("stu_data.json")
semester = "17-18-1"
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
    query = "SELECT * FROM ec_available_semesters WHERE xh=%s"
    cursor.execute(query, (each_student['xh'],))
    fetch_result = cursor.fetchall()
    if not fetch_result:
        # New student
        semesters = [semester]
        query = "INSERT INTO ec_available_semesters (xh,semesters) VALUES (%s, %s) "
        cursor.execute(query, (each_student['xh'], json.dumps(semesters)))
    else:
        # old student
        if DEBUG:
            print('Existing student: [%s]%s' % (each_student['xh'], each_student['xm']))
        semesters = json.loads(fetch_result[0][1])
        if semester not in semesters:
            # 当前学期不在数据库中则加入(不判断的话可能重复加入)
            semesters.append(semester)
            query = "UPDATE ec_available_semesters SET semesters=%s WHERE xh=%s"
            cursor.execute(query,(json.dumps(semesters),each_student['xh']))
            print("Add semester to student [%s]%s 's record" % (each_student['xh'], each_student['xm']))
    count = count + 1
    if count % 100 == 0:
        cprint('Finished %s entries.' % count, color='blue', attrs=["bold"])
conn.commit()
cursor.close()
conn.close()
cprint("Finished!(Total %s)" % count, color='blue', attrs=["bold"])

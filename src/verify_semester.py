"""
del_wrong_semester.py
Created: 2017-10-16 by Frederic
Description:
学生毕业以后，下学期前几次导入课表可能仍然在stu_data.json中，使用process_data.py导入之后这些学生就被存入ec_students表中了。
而下次导入前会清空学期表，而他们已经不在学期表中了，但ec_students表中仍然存在他们错误的学期，所以访问会出错。解决办法：导入后手
动使用 del_wrong_semester.py 清除ec_students表中错误的学期信息。
"""
import mysql.connector
import settings
import json
import predefined
from termcolor import cprint


def verify():
    conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor2 = conn.cursor()

    query = "select xh,semesters from ec_students"
    cursor.execute(query)
    students = cursor.fetchall()
    for each_student in students:
        xh = each_student[0]
        semesters = json.loads(each_student[1])
        for each_semester in semesters:
            query = "select * from ec_students_" + predefined.get_semester_code_for_db(each_semester) + " where xh=%s"
            cursor2.execute(query, (xh,))
            stu_result = cursor2.fetchall()

            if not stu_result:
                print("Remove %s in %s" % (each_semester, xh))
                query = "UPDATE ec_students SET semesters=%s WHERE xh=%s"
                semesters.remove(each_semester)
                cursor2.execute(query, (json.dumps(semesters), xh))
                conn.commit()


if __name__ == "__main__":
    verify()

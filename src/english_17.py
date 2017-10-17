# This module retrieves separate English class tables from server and process information
# Created Apr. 20, 2017 by Frederic
import requests
import json
import mysql.connector
import settings
import predefined
import hashlib
import re
from termcolor import cprint

class_dict = {}
header_info = {
    "User-Agent": settings.USER_AGENT,
    'Host': '122.207.65.163',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Cookie': settings.COOKIE_ENG,
}


def retrieve_and_process(xq):
    url = settings.ENGLISH_CLASS_URL_17
    s = requests.session()
    conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
    cursor = conn.cursor()
    print('Fetching class information...')
    req = s.post(url, headers=header_info)
    json_string = req.content.decode('utf-8')
    # predefined.print_formatted_info("Fetched json_string:" + json_string, True)
    json_content = json.loads(json_string)
    for each in json_content["courseInfo"]:
        print(each)
    for each in json_content["docs"]:
        print(each)

    for class_number in range(len(json_content["courseInfo"])):
        this_course = json_content["courseInfo"][class_number]
        this_clsname = "英语约课" + str(class_number + 1) + "班"
        this_day = predefined.get_day_for_class(this_course["courseTime"][1:3])
        this_time = predefined.get_time_for_class(this_course["courseTime"][4:7])  # 这里切片实际上是有问题的，"9-10"会切成"9-1"，之前被坑过了

        # Search in docs for teacher name
        for each in json_content["docs"]:
            if each["courseNo"] == class_number + 1 + 300:
                this_teacher = each["teacherName"]
                break

        if this_course["courseTime"][0] == '双':
            this_duration = "4-16"
            this_week = "双周"
        else:
            this_duration = "3-15"
            this_week = "单周"
        this_location = this_course["classroom"]

        # Generate MD5
        md5 = hashlib.md5()
        class_str = str(this_clsname) + \
                    str(this_teacher) + \
                    str(this_duration) + \
                    str(this_week) + \
                    str(this_location) + \
                    str(this_day) + \
                    str(this_time)
        md5.update(class_str.encode('utf-8'))
        this_id = md5.hexdigest()
        del md5

        class_dict[class_number] = dict(Clsname=this_clsname, Day=this_day, Time=this_time,
                                        Teacher=this_teacher, Duration=this_duration,
                                        Week=this_week, ID=this_id)

        query = "select * from ec_classes_" + predefined.get_semester_code_for_db(xq) + " where id=%s"
        cursor.execute(query, (this_id,))
        class_fetch_result = cursor.fetchall()
        if not class_fetch_result:
            # Add new class
            cprint('[Add class]', "blue", attrs=["bold"], end='')
            query = "INSERT INTO ec_classes_" + predefined.get_semester_code_for_db(
                xq) + " (clsname, day, time, teacher, duration, week, location, students, id) "" \
                ""VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            predefined.print_formatted_info("SQL: " + query)
            cursor.execute(query, (this_clsname,
                                   this_day,
                                   this_time,
                                   this_teacher,
                                   this_duration,
                                   this_week,
                                   this_location,
                                   json.dumps(list()),
                                   this_id)
                           )
            conn.commit()
        else:
            cprint("[Class already exists]", "green", attrs=["bold"])
        predefined.print_formatted_info(class_dict[class_number])
        print("--\n")

    # Process student
    students_list = []
    class_list = []
    for each_people in json_content["docs"]:
        cprint("Now processing [%s]%s in class %s" % (each_people["stuID"],
                                                      each_people["stuName"],
                                                      each_people["className"]
                                                      ),
               attrs=['bold'])

        # Query ec_classes table
        query = "SELECT students FROM ec_classes_" + predefined.get_semester_code_for_db(xq) + " WHERE id=%s"
        if settings.DEBUG:
            predefined.print_formatted_info(query)
        cursor.execute(query, (class_dict[each_people["courseNo"] - 300 - 1]['ID'],))
        class_fetch_result = cursor.fetchall()
        students_list.clear()
        students_list = json.loads(class_fetch_result[0][0])

        if each_people["stuID"] not in students_list:
            # Append student to class
            cprint('[Append student to class]', end='', color='blue', attrs=['bold'])
            students_list.append(each_people["stuID"])
            query = "update ec_classes_" + predefined.get_semester_code_for_db(xq) + " set students=%s where id=%s"
            cursor.execute(query, (json.dumps(students_list), class_dict[each_people["courseNo"] - 300 - 1]['ID']))
            conn.commit()
        else:
            # Student already in this class
            cprint("[Student already in this class]", color='green', attrs=['bold'])

        # Query ec_students table
        query = "SELECT classes FROM ec_students_" + predefined.get_semester_code_for_db(xq) + " WHERE xh=%s"
        if settings.DEBUG:
            predefined.print_formatted_info(query)
        cursor.execute(query, (each_people["stuID"],))
        class_fetch_result = cursor.fetchall()
        class_list = json.loads(class_fetch_result[0][0])

        if class_dict[each_people["courseNo"] - 300 - 1]['ID'] not in class_list:
            # Append class to student's record
            class_list.append(class_dict[each_people["courseNo"] - 300 - 1]['ID'])
            query = "UPDATE ec_students_" + predefined.get_semester_code_for_db(xq) + " SET classes=%s WHERE xh=%s"
            cursor.execute(query, (json.dumps(class_list), each_people["stuID"]))
            conn.commit()
            cprint("[Add class %s to student %s's record]" % (class_dict[each_people["courseNo"] - 300 - 1]['ID'],
                                                              each_people["stuID"]),
                   color='green',
                   attrs=['bold']
                   )
        else:
            # Class already in the student's record
            cprint("[Class already in this student's record]", color='green', attrs=['bold'])
        print("\n")

    cursor.close()
    conn.close()
    cprint("Finished!", color='green', attrs=['blink', 'bold'])


if __name__ == '__main__':
    semester = input('Input a semester:')
    if not semester:
        semester = settings.SEMESTER
    retrieve_and_process(semester)

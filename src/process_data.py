# This module processes data from raw_data directory and save them to database
# Created Mar. 26, 2017 by Frederic
import os, hashlib, json, mysql.connector
from bs4 import BeautifulSoup
from . import settings, predefined
from predefined import get_row_code
from predefined import get_semester_code_for_db
from termcolor import cprint


# TODO: 可能没有对同一个学期重复导入两次的情况（更新）做处理，另外注释应该补充一下


# 获得一行课程信息
def _query_class(md5_value):
    query = "SELECT clsname,day,time,teacher,duiration,week,location,students,id FROM ec_classes_" \
            + get_semester_code_for_db(xq) + " WHERE id=%s"
    if settings.DEBUG:
        predefined.print_formatted_info(query)
    cursor.execute(query, (md5_value,))
    return cursor.fetchall()


# 增加学生到一门课程
def _append_student_to_class(stu_list, this_stu, class_id):
    if this_stu not in stu_list:  # CSU教务系统莫名可能同样课程显示两次，因此必须判断是否已经在学生列表中了，否则会导致意外情况
        stu_list.append(this_stu)
        query = "UPDATE ec_classes_" + get_semester_code_for_db(xq) + " SET students=%s WHERE id=%s"
        if settings.DEBUG:
            predefined.print_formatted_info(query)
        cursor.execute(query, (json.dumps(stu_list), class_id))
        conn.commit()
        cprint('[APPEND STUDENT]', end='', color='blue', attrs=['bold'])


# 增加一门课程
def _add_new_class(clsname, class_time, row_number, teacher, duration, week, location, md5_value):
    cprint('[ADD CLASS]', end='', color="green", attrs=['bold'])
    query = "INSERT INTO ec_classes_" + get_semester_code_for_db(
        xq) + "(clsname, day, time, teacher, duration, week, location, students, id) VALUES (" \
              "%s, %s, %s, %s, %s, %s, %s, %s, %s) "
    if settings.DEBUG:
        predefined.print_formatted_info(query)
    cursor.execute(query, (
        clsname, class_time, row_number, teacher, duration, week, location, json.dumps([stu['xh']]), md5_value))
    conn.commit()


xq = settings.GLOBAL_SEMESTER
conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
cursor = conn.cursor()
names_json = open("stu_data.json")
names = json.load(names_json)
class_info = {}
my_class_list = []
students_list = []
count = 0
for stu in names:
    print('Processing student: [%s]%s' % (stu['xh'], stu['xm']))
    file_addr = os.path.join('raw_data', stu['xs0101id'])
    file = open(file_addr + '.html', 'r')
    soup = BeautifulSoup(file, 'html.parser')
    query = 'SELECT * FROM ec_available_semesters WHERE xh=%s'
    cursor.execute(query, (stu['xh'],))
    if not cursor.fetchall():
        # 若找不到，则在 ec_available_semesters 表中新增学生
        query = "INSERT INTO ec_available_semesters (xs0101id, name, xh) VALUES (%s, %s, %s)"
        cursor.execute(query, (stu['xs0101id'], stu['xm'], stu['xh']))
        conn.commit()

    # 在学期表中寻找学生
    query = 'SELECT * FROM ec_students_' + get_semester_code_for_db(xq) + ' WHERE xh=%s'
    cursor.execute(query, (stu['xh'],))
    # 在数据库中找不到学生则增加学生
    if not cursor.fetchall():
        cprint('[ADD STUDENT]', attrs=['bold'])
        for class_time in range(1, 8):
            for row_number in range(1, 7):
                query_selector = 'div[id="' + get_row_code(row_number) + '-' + str(
                    class_time) + '-2"] a'
                for i in soup.select(query_selector):  # i 为 a 元素
                    class_info['clsname'] = i.contents[0]
                    class_info['teacher'] = 'None' if not i.select('font[title="老师"]') else \
                        i.select('font[title="老师"]')[0].string
                    class_info['duration'] = 'None' if not i.select('font[title="周次"]') else \
                        i.select('font[title="周次"]')[0].string
                    class_info['week'] = 'None' if not i.select('font[title="单双周"]') else \
                        i.select('font[title="单双周"]')[0].string
                    class_info['location'] = 'None' if not i.select('font[title="上课地点教室"]') else \
                        i.select('font[title="上课地点教室"]')[0].string
                    class_str = str(class_info['clsname']) + str(class_info['teacher']) + str(
                        class_info['duration']) + str(class_info['week']) + str(class_info['location']) + str(
                        class_time) + str(row_number)  # 生成class_str用于生成课程 MD5识别码
                    md5 = hashlib.md5()
                    md5.update(class_str.encode('utf-8'))
                    class_info['hash'] = md5.hexdigest()
                    my_class_list.append(md5.hexdigest())

                    # 查询当前课程
                    class_fetch_result = _query_class(md5.hexdigest())

                    # 如果课程不存在，增加课程
                    if not class_fetch_result:
                        _add_new_class(str(class_info['clsname']), class_time, row_number,
                                       str(class_info['teacher']), str(class_info['duration']),
                                       str(class_info['week']), str(class_info['location']),
                                       md5.hexdigest())

                    # 如果课程存在，在课程entry中增加学生
                    else:
                        _append_student_to_class(json.loads(class_fetch_result[0][7]), stu['xh'], md5.hexdigest())

                    del md5
                    print(class_info)
                    class_info.clear()
        # 对 my_class_list 去重
        class_list_final = list(set(my_class_list))
        class_list_final.sort(key=my_class_list.index)

        if settings.DEBUG:
            print('Class list(%s): %s' % (len(class_list_final), class_list_final))
            predefined.print_formatted_info(query)



        # 在学期表中新增学生
        query = "INSERT INTO ec_students_" + get_semester_code_for_db(
            xq) + " (xh, classes) VALUES (%s, %s)"
        cursor.execute(query, (stu['xs0101id'], stu['xm'], stu['xh'], json.dumps(class_list_final)))

        # 提交数据及清空 list
        conn.commit()
        my_class_list.clear()

    # TODO：数据库中已存在学生则 pass，喂这好像不对啊
    else:
        cprint('[PASS] STUDENT ALREADY EXISTS', color='green', attrs=['bold'])
    count = count + 1
    if count % 100 == 0:
        cprint('%s finished.' % count, color='green')

cursor.close()
conn.close()
cprint("Finished!", color='red')

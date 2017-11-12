# This module processes data from raw_data directory and save them to database
# Created Mar. 26, 2017 by Frederic
import os, hashlib, json, mysql.connector
from bs4 import BeautifulSoup
import predefined
import settings
from predefined import get_row_code
from predefined import get_semester_code_for_db
from termcolor import cprint

xq = settings.SEMESTER
conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
cursor = conn.cursor()
names_json = open(settings.JSON_FILE)
names = json.load(names_json)
class_info = {}
my_class_list = []
students_list = []
table1_count_add = 0
table1_count_update = 0
table1_count_pass = 0
table2_count_pass = 0
table2_count_add = 0
append_to_course_count = 0
add_new_course_count = 0
total_count = 0


# 获得一行课程信息
def _query_class(md5_value):
    query = "SELECT clsname,day,time,teacher,duration,week,location,students,id FROM ec_classes_" \
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
        cursor.execute(query, (json.dumps(stu_list), class_id))
        conn.commit()
        if settings.DEBUG:
            cprint('[APPEND STUDENT]', end='', color='blue', attrs=['bold'])
        global append_to_course_count
        append_to_course_count = append_to_course_count + 1


# 增加一门课程
def _add_new_course(clsname, class_time, row_number, teacher, duration, week, location, md5_value):
    if settings.DEBUG:
        cprint('[ADD CLASS]', end='', color="green", attrs=['bold'])
    query = "INSERT INTO ec_classes_" + get_semester_code_for_db(xq) + \
            "(clsname, day, time, teacher, duration, week, location, students, id) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
    cursor.execute(query, (clsname, class_time, row_number, teacher, duration,
                           week, location, json.dumps([stu['xh']]), md5_value))
    conn.commit()
    global add_new_course_count
    add_new_course_count = add_new_course_count + 1


for stu in names:
    if settings.DEBUG:
        cprint('Processing student: [xh=%s][xs0101id=%s]%s' % (stu['xh'], stu['xs0101id'], stu['xm']), attrs=['bold'])
    file_addr = os.path.join('raw_data', stu['xs0101id'])
    file = open(file_addr + '.html', 'r')
    soup = BeautifulSoup(file, 'html.parser')

    # ec_students 表检查
    query = 'SELECT xh,semesters FROM ec_students WHERE xh=%s'
    cursor.execute(query, (stu['xh'],))
    fetch_result = cursor.fetchall()
    if not fetch_result:
        # 若找不到，则在 ec_students 表中新增学生
        query = "INSERT INTO ec_students (xh, semesters, xs0101id, name) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (stu['xh'], json.dumps([settings.SEMESTER,]), stu['xs0101id'], stu['xm']))
        conn.commit()
        table1_count_add = table1_count_add + 1
    else:
        # 老生检查学期是否在个人记录中已经存在，若不存在则加入
        if settings.DEBUG:
            print('Existing student: [%s]%s' % (stu['xh'], stu['xm']))
        semesters = json.loads(fetch_result[0][1])
        if settings.SEMESTER not in semesters:
            # 当前学期不在数据库中则加入(不判断的话可能重复加入)
            semesters.append(settings.SEMESTER)
            query = "UPDATE ec_students SET semesters=%s WHERE xh=%s"
            cursor.execute(query, (json.dumps(semesters), stu['xh']))
            conn.commit()
            table1_count_update = table1_count_update + 1
            print("Add semester to student [%s]%s 's record" % (stu['xh'], stu['xm']))
        else:
            table1_count_pass = table1_count_pass + 1

    # ec_students 学期表中寻找学生
    query = 'SELECT * FROM ec_students_' + get_semester_code_for_db(xq) + ' WHERE xh=%s'
    cursor.execute(query, (stu['xh'],))
    # 在数据库中找不到学生则增加学生
    if not cursor.fetchall():
        if settings.DEBUG:
            print('[Add student to ec_students_%s]' % get_semester_code_for_db(xq))
        for class_time in range(1, 8):
            for row_number in range(1, 7):
                query_selector = 'div[id="' + get_row_code(xq, row_number) + '-' + str(
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
                    class_str = str(class_info['clsname']) + \
                                str(class_info['teacher']) + \
                                str(class_info['duration']) + \
                                str(class_info['week']) + \
                                str(class_info['location']) + \
                                str(class_time) + \
                                str(row_number)  # 生成class_str用于生成课程 MD5识别码
                    md5 = hashlib.md5()
                    md5.update(class_str.encode('utf-8'))
                    class_info['hash'] = md5.hexdigest()
                    my_class_list.append(md5.hexdigest())

                    # 查询当前课程
                    class_fetch_result = _query_class(md5.hexdigest())

                    # 如果课程不存在，增加课程
                    if not class_fetch_result:
                        _add_new_course(str(class_info['clsname']), class_time, row_number,
                                        str(class_info['teacher']), str(class_info['duration']),
                                        str(class_info['week']), str(class_info['location']),
                                        md5.hexdigest())

                    # 如果课程存在，在课程entry中增加学生
                    else:
                        _append_student_to_class(json.loads(class_fetch_result[0][7]), stu['xh'], md5.hexdigest())

                    del md5
                    
                    if settings.DEBUG:
                        print(class_info)
                    class_info.clear()
        # 对 my_class_list 去重
        class_list_final = list(set(my_class_list))
        class_list_final.sort(key=my_class_list.index)

        if settings.DEBUG:
            print('Class list(%s): %s' % (len(class_list_final), class_list_final))
            predefined.print_formatted_info(query)

        # 在学期表中新增学生
        query = "INSERT INTO ec_students_" + get_semester_code_for_db(xq) \
                + " (xh, classes) VALUES (%s, %s)"
        cursor.execute(query, (stu['xh'], json.dumps(class_list_final)))

        # 提交数据及清空 list
        conn.commit()
        table2_count_add = table2_count_add + 1
        my_class_list.clear()
    # 如果学期表中已经存在数据就跳过（学期表只能从零开始，不能更新）
    else:
        print('[PASS] student [%s]%s already exists in %s'
               % (stu['xh'], stu['xm'], "ec_students_" + get_semester_code_for_db(xq)))
        table2_count_pass = table2_count_pass + 1

    # 每100个处理完毕告知一次
    total_count = total_count + 1
    if total_count % 100 == 0:
        cprint('%s finished.' % total_count, color='green', attrs=["bold"])

cursor.close()
conn.close()

# 统计数据
cprint("Finished!", color='green', attrs=['bold'])
cprint("%s students in total." % total_count)
cprint("Added %s, updated %s, passed %s students in ec_students." % (table1_count_add,
                                                                     table1_count_update,
                                                                     table1_count_pass
                                                                     ))
cprint("Added %s, passed %s students in ec_students_%s." % (table2_count_add, table2_count_pass,
                                                            get_semester_code_for_db(xq)
                                                            ))
cprint("Added %s new courses, %s times append student to course." % (add_new_course_count, append_to_course_count))

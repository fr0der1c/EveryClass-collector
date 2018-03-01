"""
Processes data from raw_data directory and save them to database
"""
import os, hashlib, json, mysql.connector
from bs4 import BeautifulSoup
import predefined
import settings
import time
from predefined import get_row_code
from predefined import get_semester_code_for_db
from termcolor import cprint
from threading import Thread, Lock
from queue import Queue

xq = settings.SEMESTER
db_lock = Lock()
count_lock = Lock()

TABLE1_COUNT_ADD = TABLE1_COUNT_UPDATE = TABLE1_COUNT_PASS = TABLE2_COUNT_PASS = TABLE2_COUNT_ADD = 0
APPEND_TO_COURSE_COUNT = ADD_NEW_COURSE_COUNT = TOTAL_COUNT = 0
queue = Queue(0)

num_worker_threads = 5


# 获得一行课程信息
def _query_class(md5_value, cursor):
    query = "SELECT clsname,day,time,teacher,duration,week,location,students,id FROM ec_classes_" \
            + get_semester_code_for_db(xq) + " WHERE id=%s"
    if settings.DEBUG_LEVEL >= 3:
        predefined.print_formatted_info(query)

    cursor.execute(query, (md5_value,))
    result = cursor.fetchall()
    return result


# 增加学生到一门课程
def _append_student_to_class(existing_students, this_student, class_id, cursor, conn):
    global APPEND_TO_COURSE_COUNT
    if this_student not in existing_students:  # CSU教务系统莫名可能同样课程显示两次，因此必须判断是否已经在学生列表中了，否则会导致意外情况
        existing_students.append(this_student)
        query = "UPDATE ec_classes_" + get_semester_code_for_db(xq) + " SET students=%s WHERE id=%s"
        cursor.execute(query, (json.dumps(existing_students), class_id))
        conn.commit()

        if settings.DEBUG_LEVEL >= 2:
            cprint('[APPEND STUDENT]', color='blue', attrs=['bold'])

        count_lock.acquire()
        APPEND_TO_COURSE_COUNT = APPEND_TO_COURSE_COUNT + 1
        count_lock.release()


# 增加一门课程
def _add_new_course(course_name, class_time, row_number, teacher, duration, week, location, md5_value, xh, cursor,
                    conn):
    global ADD_NEW_COURSE_COUNT
    if settings.DEBUG_LEVEL >= 2:
        cprint('[ADD CLASS]', color="green", attrs=['bold'])
    query = "INSERT INTO ec_classes_" + get_semester_code_for_db(xq) + \
            "(clsname, day, time, teacher, duration, week, location, students, id) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
    cursor.execute(query, (course_name, class_time, row_number, teacher, duration,
                           week, location, json.dumps([xh]), md5_value))
    conn.commit()

    count_lock.acquire()
    ADD_NEW_COURSE_COUNT = ADD_NEW_COURSE_COUNT + 1
    count_lock.release()


class ProcessThread(Thread):
    def __init__(self, thread_id):
        super().__init__()
        self.thread_id = thread_id

    def run(self):
        global TABLE1_COUNT_ADD, TABLE1_COUNT_PASS, TABLE1_COUNT_UPDATE, TABLE2_COUNT_ADD, TABLE2_COUNT_PASS
        global TOTAL_COUNT, ADD_NEW_COURSE_COUNT, APPEND_TO_COURSE_COUNT
        conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
        cursor = conn.cursor()

        while True:
            my_courses_md5 = []

            stu = queue.get()
            if stu is None:
                print("Thread %s quit." % self.thread_id)
                cursor.close()
                break

            if settings.DEBUG_LEVEL >= 1:
                print('Processing student: [xh=%s][xs0101id=%s]%s' % (stu['xh'], stu['xs0101id'], stu['xm']))

            # Read file
            file_address = os.path.join('raw_data', stu['xs0101id'])
            file = open(file_address + '.html', 'r')
            soup = BeautifulSoup(file, 'html.parser')

            # ec_students 表检查
            db_lock.acquire()
            query = 'SELECT xh,semesters FROM ec_students WHERE xh=%s'
            cursor.execute(query, (stu['xh'],))
            fetch_result = cursor.fetchall()
            db_lock.release()

            if not fetch_result:
                # 若找不到，则在 ec_students 表中新增学生
                db_lock.acquire()
                query = "INSERT INTO ec_students (xh, semesters, xs0101id, name) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (stu['xh'], json.dumps([settings.SEMESTER, ]), stu['xs0101id'], stu['xm']))
                conn.commit()
                cprint('[ec_students] add new student [%s]%s' % (stu['xh'], stu['xm']))
                db_lock.release()

                count_lock.acquire()
                TABLE1_COUNT_ADD = TABLE1_COUNT_ADD + 1
                count_lock.release()

            else:
                # 老生检查学期是否在个人记录中已经存在，若不存在则加入
                semesters = json.loads(fetch_result[0][1])
                if settings.SEMESTER not in semesters:
                    # 当前学期不在数据库中则加入(不判断的话可能重复加入)
                    semesters.append(settings.SEMESTER)

                    db_lock.acquire()
                    query = "UPDATE ec_students SET semesters=%s WHERE xh=%s"
                    cursor.execute(query, (json.dumps(semesters), stu['xh']))
                    conn.commit()
                    db_lock.release()

                    count_lock.acquire()
                    TABLE1_COUNT_UPDATE = TABLE1_COUNT_UPDATE + 1
                    count_lock.release()
                    cprint("[ec_students] Add semester to student [%s]%s 's record" % (stu['xh'], stu['xm']))
                else:
                    count_lock.acquire()
                    TABLE1_COUNT_PASS = TABLE1_COUNT_PASS + 1
                    count_lock.release()
                    cprint("[ec_students] Semester already in student [%s]%s 's record" % (stu['xh'], stu['xm']))

            # 学期表中寻找学生
            db_lock.acquire()
            query = 'SELECT * FROM ec_students_' + get_semester_code_for_db(xq) + ' WHERE xh=%s'
            cursor.execute(query, (stu['xh'],))
            result = cursor.fetchall()
            db_lock.release()

            # 在数据库中找不到学生，则增加学生
            if not result:
                if settings.DEBUG_LEVEL >= 2:
                    print('[ec_students_%s] Add student [%s]%s' % (get_semester_code_for_db(xq), stu['xh'], stu['xm']))
                for class_time in range(1, 8):
                    for row_number in range(1, 7):
                        query_selector = 'div[id="' + get_row_code(xq, row_number) + '-' + str(
                            class_time) + '-2"] a'
                        for i in soup.select(query_selector):  # i 为 a 元素
                            course_info = {'clsname': i.contents[0],
                                           'teacher': 'None' if not i.select('font[title="老师"]') else \
                                               i.select('font[title="老师"]')[0].string,
                                           'duration': 'None' if not i.select('font[title="周次"]') else \
                                               i.select('font[title="周次"]')[0].string,
                                           'week': 'None' if not i.select('font[title="单双周"]') else \
                                               i.select('font[title="单双周"]')[0].string,
                                           'location': 'None' if not i.select('font[title="上课地点教室"]') else \
                                               i.select('font[title="上课地点教室"]')[0].string}

                            class_str = str(course_info['clsname']) + \
                                        str(course_info['teacher']) + \
                                        str(course_info['duration']) + \
                                        str(course_info['week']) + \
                                        str(course_info['location']) + \
                                        str(class_time) + \
                                        str(row_number)  # 生成class_str用于生成课程 MD5识别码
                            md5 = hashlib.md5()
                            md5.update(class_str.encode('utf-8'))
                            course_info['hash'] = md5.hexdigest()
                            my_courses_md5.append(md5.hexdigest())

                            db_lock.acquire()
                            # 查询当前课程
                            class_fetch_result = _query_class(md5.hexdigest(), cursor)

                            # 如果课程不存在，增加课程
                            if not class_fetch_result:
                                _add_new_course(course_name=str(course_info['clsname']),
                                                class_time=class_time,
                                                row_number=row_number,
                                                teacher=str(course_info['teacher']),
                                                duration=str(course_info['duration']),
                                                week=str(course_info['week']),
                                                location=str(course_info['location']),
                                                md5_value=md5.hexdigest(),
                                                xh=stu['xh'],
                                                cursor=cursor,
                                                conn=conn)

                            # 如果课程存在，在课程entry中增加学生
                            else:
                                _append_student_to_class(existing_students=json.loads(class_fetch_result[0][7]),
                                                         this_student=stu['xh'],
                                                         class_id=md5.hexdigest(),
                                                         cursor=cursor,
                                                         conn=conn)
                            db_lock.release()

                            del md5

                            if settings.DEBUG:
                                print(course_info)

                # 对 my_courses_md5 去重
                class_list_final = list(set(my_courses_md5))
                class_list_final.sort(key=my_courses_md5.index)

                if settings.DEBUG_LEVEL >= 3:
                    print('Courses list(%s): %s' % (len(class_list_final), class_list_final))
                    predefined.print_formatted_info(query)

                # 在学期表中新增学生
                db_lock.acquire()
                query = "INSERT INTO ec_students_" + get_semester_code_for_db(xq) \
                        + " (xh, classes) VALUES (%s, %s)"
                cursor.execute(query, (stu['xh'], json.dumps(class_list_final)))
                conn.commit()
                db_lock.release()

                # 提交数据及清空 list
                count_lock.acquire()
                TABLE2_COUNT_ADD = TABLE2_COUNT_ADD + 1
                count_lock.release()

            # 如果学期表中已经存在数据就跳过（学期表只能从零开始，不能更新）
            else:
                cprint('[%s] student [%s]%s already exists, pass. This is unexpected behaviour!'
                       % ("ec_students_" + get_semester_code_for_db(xq), stu['xh'], stu['xm']), color='red')

                count_lock.acquire()
                TABLE2_COUNT_PASS = TABLE2_COUNT_PASS + 1
                count_lock.release()

            # 每100个处理完毕告知一次
            count_lock.acquire()
            TOTAL_COUNT = TOTAL_COUNT + 1
            count_lock.release()

            if TOTAL_COUNT % 100 == 0:
                cprint('%s finished.' % TOTAL_COUNT, color='green', attrs=["bold"])

            queue.task_done()


def process():
    with open("stu_data_version.json") as f:
        JSON_FILE = json.load(f)["stu_data_json_name"]
    names_json = open(JSON_FILE)
    names = json.load(names_json)

    # Put student in queue
    for stu in names:
        queue.put(stu)

    # Create threads and starts them
    threads = [ProcessThread(i) for i in range(num_worker_threads)]
    for each_thread in threads:
        each_thread.start()

    # block until all tasks are done
    queue.join()

    # stop workers
    for i in range(num_worker_threads):
        queue.put(None)
    for each_thread in threads:
        each_thread.join()

    # Statistics
    cprint("Finished!", color='green', attrs=['bold'])
    cprint("%s students in total." % TOTAL_COUNT)
    cprint("Added %s, updated %s, passed %s students in ec_students." % (TABLE1_COUNT_ADD,
                                                                         TABLE1_COUNT_UPDATE,
                                                                         TABLE1_COUNT_PASS
                                                                         ))
    cprint("Added %s, passed %s students in ec_students_%s." % (TABLE2_COUNT_ADD, TABLE2_COUNT_PASS,
                                                                get_semester_code_for_db(xq)
                                                                ))
    cprint("Added %s new courses, %s times append student to course." % (ADD_NEW_COURSE_COUNT, APPEND_TO_COURSE_COUNT))


if __name__ == "__main__":
    process()

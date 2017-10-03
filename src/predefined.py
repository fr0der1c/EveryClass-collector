# -*- coding: utf-8 -*-
# This file contains predefined information which needs to be imported by other modules
# Created Apr. 19, 2017 by Frederic
from termcolor import cprint


# Function: get_row_code
# Used to get row code for each row in separate files in raw_data. The value will change
# when educational management system refreshes data.
# Usage example: get_row_code(1)
def get_row_code(semester, row_num):
    row_codes = {
        '2016-2017-2': ['0',
                        'BFCA2900002E48B1B20AD34D4E4E50C8',
                        '11DD7A497F57416EA11C4D01AD1DA66A',
                        'A777C6C778AB462BB742C6640D58E0DD',
                        '1AC61925F56341B494CBA5AEA3C4AC3B',
                        'ADD7F6354105427EBA9EE72883DAF69F',
                        '921723A66500482189BDEF39E4C87D61'
                        ],
        '2017-2018-1': ['0',
                        '1A1D906AA5764D3B8EE7DBB72C825D37',
                        'B276E5D4A2414CAE95C3D5D0261DDAD9',
                        '6EBE1D8AF0BC4A19B032EDB30BF9DBE1',
                        '13AA72C5C821491792E98546D9E5F4C6',
                        '04930EB79BF748879F01CE4C672D304B',
                        'CC2AF831EFD7458BB24437E0FA7BC55D']
    }
    return row_codes[semester][row_num]


# Function: semester_code
# For tables like ec_students or ec_classes, each semesters will have their own
# tables to reduce server pressure while querying. For example, the student table for second semester during 2016 and
#  2017 will be "ec_students_16_17_2". This function transforms semester codes like "2016-2017-2" to table name type
# like "16_17_2"
# Usage:
# Example: semester_code("2016-2017-2")
def get_semester_code_for_db(xq):
    if xq == '':
        import settings
        return get_semester_code_for_db(settings.SEMESTER)
    else:
        import re
        splited = re.split('-', xq)
        return str(splited[0][2:4] + "_" + splited[1][2:4] + "_" + splited[2])


# Function: get_day_for_class
# Used to transform day like "周一" to digital form "1"
# Usage:
# Example: get_day_for_class("周一")
def get_day_for_class(chinese):
    if chinese == '周一':
        return '1'
    elif chinese == '周二':
        return '2'
    elif chinese == '周三':
        return '3'
    elif chinese == '周四':
        return '4'
    elif chinese == '周五':
        return '5'
    elif chinese == '周六':
        return '6'
    else:
        return '7'


# Function: get_time_for_class
# Used to transform time like "1-2" to form "1"
# Usage:
# Example: get_time_for_class("1-2")
#    Parameter is expected to be "1-2", "3-4", "5-6", "7-8", "9-10", "11-12"
def get_time_for_class(text):
    if text == '1-2':
        return '1'
    elif text == '3-4':
        return '2'
    elif text == '5-6':
        return '3'
    elif text == '7-8':
        return '4'
    elif text == '9-10':
        return '5'
    elif text == '9-1':
        return '5'
    else:
        return '6'


# Function: print_formatted_info
# Used to print debug info
# Usage:
# 1. print_formatted_info([list, dict and so on data types])
#    Won't show "---DEBUG---" flags
# 2. print_formatted_info([list, dict and so on data types],True)
#    Will show "---DEBUG---" flags
def print_formatted_info(info, show_debug_tip=False, info_about="DEBUG"):
    if show_debug_tip:
        cprint("-----" + info_about + "-----", "blue", attrs=['bold'])
    if isinstance(info, dict):
        for (k, v) in info.items():
            print("%s =" % k, v)
    elif isinstance(info, str):
        cprint(info, attrs=["bold"])
    else:
        for each_info in info:
            print(each_info)
    if show_debug_tip:
        cprint("----" + info_about + " ENDS----", "blue", attrs=['bold'])


# Function: create_tables
# Used to create tables for a semester
def create_tables():
    import mysql.connector
    from . import settings
    conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
    cursor = conn.cursor()
    try:
        for line in open('everyclass.sql', 'r'):
            cursor.execute(line)
    except mysql.connector.errors.DatabaseError as e:
        cprint("Mysql Exception %d: %s" % (e.args[0], e.args[1]), "red")
    conn.commit()
    conn.close()

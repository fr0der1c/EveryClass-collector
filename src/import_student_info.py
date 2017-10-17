import xlrd
import mysql.connector
import settings

conn = mysql.connector.connect(**settings.MYSQL_CONFIG)
cursor = conn.cursor()

print("Reading...")
data = xlrd.open_workbook('student_information.xlsx')
table = data.sheets()[0]
nrows = table.nrows
print("Read successful.")
for row in range(nrows):
    cell = table.row_values(row)

    # Select student in database
    query = "SELECT xh,faculty,class_name FROM ec_students WHERE xh=%s"
    cursor.execute(query, (cell[0],))
    stu_result = cursor.fetchall()

    # If in database, update its faculty and class information.
    if stu_result:
        query = "UPDATE ec_students SET faculty=%s,class_name=%s WHERE xh=%s"
        cursor.execute(query, (cell[8], cell[13], cell[0]))
        print("update ",cell[0], cell[1], cell[8], cell[13])
        conn.commit()

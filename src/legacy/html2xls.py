import json
import xlwt
file = open("stu_data.json")
data = json.load(file)
wb = xlwt.Workbook()
sh = wb.add_sheet('全校学生数据')
sh.write(0, 0, "xs0101id")
sh.write(0, 1, "学号")
sh.write(0, 2, '姓名')
i = 1
for x in data:
    sh.write(i, 0, x['xs0101id'])
    sh.write(i, 1, x['xh'])
    sh.write(i, 2, x['xm'])
    i += 1
    print(x)
wb.save('example.xls')

import json

with open("stu_data.json") as f:
    students = json.load(f)
print(len(students))

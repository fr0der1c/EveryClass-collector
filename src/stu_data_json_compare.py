import json
import settings

with open("stu_data_1029.json") as old_file:
    with open("stu_data_1112.json") as new_file:
        old = json.load(old_file)
        new = json.load(new_file)
        print("Old length:%d" % len(old))
        print("New length:%d" % len(new))
        print("In old but not in new:")
        for each in old:
            if each not in new:
                print(each)
        print("In new but not in old")
        for each in new:
            if each not in old:
                print(each)

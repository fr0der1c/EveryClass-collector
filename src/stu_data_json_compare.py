import json
import settings


def compare_json(old, new):
    with open(old) as old_file:
        with open(new) as new_file:
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


if __name__ == "__main__":
    compare_json(old="stu_data_1029.json", new="stu_data_1112.json")

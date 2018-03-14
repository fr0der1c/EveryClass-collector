import json
import glob
import os


def compare():
    with open('stu_data_20180307.json') as json_file:
        json_file = json.load(json_file)
        files = os.listdir(os.path.join(os.getcwd(), 'raw_data'))

        print("Json length:%d" % len(json_file))
        print("File count:%d" % len(files))
        print("In json but not in folder:")
        for each in json_file:

            if each['xs0101id'] + '.html' not in files:
                print(each)

        print("\nIn folder but not in json")
        for each in files:
            xs0101id = each.split('.')[0]
            found = False
            for i in json_file:
                if i['xs0101id'] == xs0101id:
                    found = True
            if not found:
                print(each)


if __name__ == "__main__":
    compare()

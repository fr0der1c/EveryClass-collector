# This file contains global settings of data_collector
# Created Apr. 19, 2017 by Frederic
import json
SEMESTER = "2017-2018-1"
with open("stu_data_version.json") as f:
    JSON_FILE = json.load(f)["stu_data_json_name"]
DEBUG = False
DEBUG_LEVEL = 0  # 5 means most

# MySQL Config
MYSQL_CONFIG = {
    'user': 'everyclass_user',
    'password': 'everyclass_pwd',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'everyclass',
    'raise_on_warnings': True,
}

# Network settings
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8'
COOKIE_JW = 'JSESSIONID=A32385D45A9A042BC42BB92F0FF6312D; BIGipServerpool_jwctest=2034746826.20480.0000'
COOKIE_ENG = 'ASPSESSIONIDCAQTSACT=LHBFPBODGNPMGHEPJNLDBNLM; ASP.NET_SessionId=xpud3z45w1hh5i45j4ptf5vd; ASPSESSIONIDCATQSBCT=CDPNOMLDGEHKJGDHDLMJJNEC'
ENGLISH_CLASS_URL = 'http://122.207.65.163/agent161/remote/get_englishClass_2017.asp'
ENGLISH_CLASS_NAMEROLL_URL = 'http://122.207.65.163/agent161/remote/get_englishClass_nameroll_2017.asp'
ENGLISH_CLASS_URL_17 = 'http://122.207.65.163/nodejs2/db/mobile/classes.js?%7B%22search%22:%7B%22courseNo%22:%7B%22$gt%22:300%7D%7D,%22fields%22:%7B%22_id%22:0%7D,%22options%22:%7B%22limit%22:4060,%22skip%22:0%7D%7D'

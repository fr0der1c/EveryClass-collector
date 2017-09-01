# This file contains global settings of data_collector
# Created Apr. 19, 2017 by Frederic
SEMESTER = "2017-2018-1"
DEBUG = False

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
COOKIE_JW = 'JSESSIONID=F1E37484CA68AED53C0D9BA3535372E4; BIGipServerpool_jwctest=2017969610.20480.0000'
COOKIE_ENG = 'ASPSESSIONIDCAQTSACT=LHBFPBODGNPMGHEPJNLDBNLM; ASP.NET_SessionId=xpud3z45w1hh5i45j4ptf5vd; ASPSESSIONIDCATQSBCT=CDPNOMLDGEHKJGDHDLMJJNEC'
ENGLISH_CLASS_URL = 'http://122.207.65.163/agent161/remote/get_englishClass_2017.asp'
ENGLISH_CLASS_NAMEROLL_URL = 'http://122.207.65.163/agent161/remote/get_englishClass_nameroll_2017.asp'
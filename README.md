## Data-collecting part of EveryClass
EveryClass 数据收集模块

This is the data collecting part of EveryClass. We decided to separate its different module to standalone repositories for clearer structure. See [project page](https://github.com/fr0der1c/EveryClass) for more information. Since this repo is specially for Chinese school students, we do not offer English version of this README document.

To run this python programme, please use Python 3.6.0

### 源码使用指南


#### 数据库和基础设置
- 配置settings.py中的当前学期、数据库等信息；
- 导入 `sql/everyclass.sql` 内的数据到mysql数据库，你可能需要修改学期信息。如果你不知道怎么导入，你可以将它拷贝到`data_collector`目录中，然后在python shell中：
```
>>> from predefined import create_tables
>>> create_tables()
```

#### 学生信息采集
- 通过各种手段取得包含学生基本信息的stu_data.json，保存在data_collector目录下（格式参见stu_data_sample.json，出于对本校学生信息的保护，恕不直接提供stu_data.json文件）

#### 教务数据获取和处理
- 手动通过浏览器操作进入教务的课表查询页面，然后抓包获得 cookies，修改`settings.py`里的`COOKIE_JW`字段（因为教务系统有非常严格的 session 机制，在每次运行 retrieve.py 前请务必先确认你此时通过浏览器能正常访问课表查询界面，然后将 cookies 填入`settings.py`）
- 马上运行`retrieve.py`，它将会按照`stu_data.json`里的列表从教务系统爬取课表存放在`data_collector/raw_data`文件夹里，这大概需要耗费10小时的时间
- 运行`process_data.py`，程序将会通过 Python 的 Beautiful Soup 4 库分析raw_data文件夹里的 HTML 页面，并将课程和学生信息写入数据库

#### 英语大班课单独导入
- 英语大班课没有录入教务系统，因此单独运行english_class.py，程序会获取大班课信息然后保存到数据库
- 如果无法获取数据请先抓包获得 cookies 然后填入`settings.py`的`COOKIE_ENG`字段

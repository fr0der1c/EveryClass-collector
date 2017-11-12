# This module retrieves class tables from server and save them to raw_data directory
# Created Mar. 15, 2017 by Frederic
import requests
import json
import settings
from termcolor import cprint
from threading import Thread
from queue import Queue

url = 'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp'
num_worker_threads = 5
header_info = {
    "User-Agent": settings.USER_AGENT,
    "Referer": "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xs0101.jsp?xnxq01id=2016-2017-2&init=1&isview=0",
    'Host': 'csujwc.its.csu.edu.cn',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-cn',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://csujwc.its.csu.edu.cn',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Content-Length': '103',
    'Cookie': settings.COOKIE_JW,
}
queue = Queue(0)


class SpiderThread(Thread):
    def __init__(self, thread_id):
        super().__init__()
        self.thread_id = thread_id

    def run(self):
        while True:
            this = queue.get()
            if this is None:
                break

            s = requests.session()
            data = {'type': 'xs0101', 'isview': '0', 'xnxq01id': settings.SEMESTER, 'xs0101id': this['xs0101id'],
                    'xs': this['xs'], 'sfFD': '1'}

            print('Trying to fetch data for %s...' % this)
            req1 = s.post(url, headers=header_info, data=data)
            local_filename = 'raw_data/' + data['xs0101id'] + '.html'
            with open(local_filename, 'wb') as f:
                f.write(req1.content)
            print(req1)

            queue.task_done()


def retrieve():
    file = open(settings.JSON_FILE)
    stu_data = json.load(file)

    # Add task to queue
    for i in stu_data:
        queue.put({'xs0101id': i['xs0101id'],
                   'xs': i['xm']})
    cprint('Task scheduling finished.', color='green')

    # Create threads and starts them
    threads = [SpiderThread(i) for i in range(num_worker_threads)]
    for each_thread in threads:
        each_thread.start()

    # block until all tasks are done
    queue.join()

    # stop workers
    for i in range(num_worker_threads):
        queue.put(None)
    for each_thread in threads:
        each_thread.join()

    cprint('Finished.', color='green')


if __name__ == '__main__':
    retrieve()

#!/usr/bin python
# -*- coding: utf-8 -*-
import threading
from common import MyQueue
from dehy import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# http://www.dehyc.com
queue = MyQueue.MyQueue(200000)
thread_count = 1


class HandleThread(threading.Thread):

    def __init__(self, name, queue):
        threading.Thread.__init__(self, name=name)
        self.t_name = name
        self.t_queue = queue

    def run(self):
        while(True):
            try:
                print queue.qsize()
                obj = queue.get(timeout=30)
                obj.run()
            except Exception as e:
                print threading.current_thread().getName(), '---conti'
                pass

if __name__ == '__main__':

    for i in range(0, thread_count):
        worker = HandleThread("work-%s" % (i), queue)
        worker.start()
#     sound.SoundParse(queue)
    text.textParse(queue)

#!/usr/bin/python
# -*-coding:utf-8-*-
from Queue import Queue


class MyQueue(Queue):
    '''
    继承python库的Queue  添加clear 方法
    '''

    def __init__(self, maxsize=0):
        '''
        构造函数
        '''
        Queue.__init__(self, maxsize)

    def clear(self):
        '''
        clear方法，清空队列
        '''
        self.not_empty.acquire()
        try:
            while self._qsize() != 0:
                self._get()
            self.not_full.notify()

        finally:
            self.not_empty.release()

    def get(self, block=True, timeout=None):
        try:
            return Queue.get(self, block, timeout)
        except Exception as e:
            return None

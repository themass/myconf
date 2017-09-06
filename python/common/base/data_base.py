#!/usr/bin/python
# -*-coding:utf-8-*-
import MySQLdb
import datetime
from common import dateutil
from common import typeutil
from common import common


class DataBase(object):

    def __init__(self, host, port, user, passwd, db):
        self.conn = MySQLdb.connect(
            host=host, port=port, user=user, passwd=passwd, db=db, charset='utf8')
        self.cur = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        self.__level = False

    def execute(self, query, args=None):
        if args != None and isinstance(args, list):
            typeutil.listReplace(args, None, -1)
        if query.count('%s') != 0 and query.count('%s') != len(args):
            print 'error: sql error[%s][%s]' % (query, args)
            raise ValueError('error: sql error[%s][%s]' % (query, args))
        if self.__level == True:
            if args != None:
                print ('%s:[%s]') % (query, args)
            else:
                print query
        try:
            return self.cur.execute(query, args)
        except Exception as e:
            #             print common.format_exception(e)
            return None

    def commit(self):
        self.conn.commit()

    def setPrintSql(self, level):
        self.__level = level

    def fetchOne(self):
        ret = self.cur.fetchone()
        return self.handleType(ret)

    def fetchAll(self):
        data = []
        ret = self.cur.fetchall()
        for item in ret:
            data.append(self.handleType(item))
        return data

    def handleType(self, ret):
        data = {}
        if ret != None:
            for key, val in ret.items():
                if isinstance(val, datetime.datetime):
                    data[key] = dateutil.formatdate(val)
                elif isinstance(val, unicode):
                    data[key] = val
                else:
                    data[key] = val
        return data

    def close(self):
        return self.conn.close()

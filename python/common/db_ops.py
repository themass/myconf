#!/usr/bin/env python
# coding=utf-8
import MySQLdb


class DbOps(object):

    def __init__(self, conn):
        self.conn = conn

    def inertSoundChannel(self, obj):
        self.conn.execute(
            "replace into  soundchannel (name,baseurl,url,pic,updateTime) values ('%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("pic"), obj.get("updateTime")))

    def inertSoundFile(self, obj):
        self.conn.execute(
            "replace into  sounditems (name,baseurl,url,channel,file,fileDate,updateTime) values ('%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("file"), obj.get("fileDate"), obj.get("updateTime")))

    def inertTextChannel(self, obj):
        self.conn.execute(
            "replace into  textchannel (name,baseurl,url,updateTime) values ('%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("updateTime")))

    def inertTextFile(self, obj):
        self.conn.execute(
            "replace into  textitems (name,baseurl,url,channel,file,fileDate,updateTime) values ('%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), MySQLdb.escape_string(obj.get("file")), obj.get("fileDate"), obj.get("updateTime")))

    def getTextChannel(self):
        self.conn.execute("select * from  textchannel")
        return self.conn.fetchAll()

    def getTextChannelItems(self, channel):
        self.conn.execute(
            "select * from  textitems where channel=%s" % (channel))
        return self.conn.fetchAll()

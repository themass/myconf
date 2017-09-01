#!/usr/bin/env python
# coding=utf-8
import MySQLdb


class DbOps(object):

    def __init__(self, conn):
        self.conn = conn

    def inertSoundChannel(self, obj):
        self.conn.execute(
            "replace into  soundchannel (name,baseurl,url,pic,updateTime,rate) values ('%s','%s','%s','%s','%s',1.1)"
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

    def getTextChannelItems(self, channel, i):
        start = i * 20
        end = (i + 1) * 20
        self.conn.execute(
            "select * from  textitems where channel='%s' and id>21118 order by id desc  limit %s,%s " % (channel, start, end))
        return self.conn.fetchAll()

    def inertImgChannel(self, obj):
        self.conn.execute(
            "replace into  imgchannel (name,baseurl,url,updateTime) values ('%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("updateTime")))

    def inertImgItems(self, obj):
        self.conn.execute(
            "replace into  imgitems (name,baseurl,url,channel,fileDate,pics,updateTime) values ('%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("fileDate"), obj.get("pics"), obj.get("updateTime")))

    def inertImgItems_item(self, obj):
        self.conn.execute(
            "replace into  imgitems_item (picUrl,itemUrl) values ('%s','%s')"
            % (obj.get("picUrl"), obj.get("itemUrl")))

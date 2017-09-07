#!/usr/bin/env python
# coding=utf-8
import MySQLdb


class DbOps(object):

    def __init__(self, conn):
        self.conn = conn

    def inertSoundChannel(self, obj):
        return self.conn.execute(
            "replace into  soundchannel (name,baseurl,url,pic,updateTime,rate) values ('%s','%s','%s','%s','%s',%s)"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("pic"), obj.get("updateTime"), 1.1))

    def inertSoundItems(self, obj):
        return self.conn.execute(
            "insert into  sounditems (name,baseurl,url,channel,file,fileDate,updateTime,sortType) values ('%s','%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("file"), obj.get("fileDate"), obj.get("updateTime"), obj.get("sortType")))

    def inertTextChannel(self, obj):
        return self.conn.execute(
            "replace into  textchannel (name,baseurl,url,updateTime) values ('%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("updateTime")))

    def inertTextItems(self, obj):
        return self.conn.execute(
            "insert into  textitems (name,baseurl,url,channel,fileDate,updateTime,sortType) values ('%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("fileDate"), obj.get("updateTime"), obj.get("sortType")))

    def inertTextItems_item(self, obj):
        return self.conn.execute(
            "replace into  textitems_item (fileUrl,file) values ('%s','%s')"
            % (
                obj.get("fileUrl"), MySQLdb.escape_string(obj.get("file"))))

    def getTextChannel(self):
        self.conn.execute("select * from  textchannel")
        return self.conn.fetchAll()

    def getTextChannelItems(self, channel, i):
        start = i * 20
        end = (i + 1) * 20
        self.conn.execute(
            "select * from  textitems where channel='%s' order by id asc  limit %s,%s " % (channel, start, end))
        return self.conn.fetchAll()

    def getTextChannelItemsById(self, i, sortType):
        start = i * 20
        end = (i + 1) * 20
        self.conn.execute(
            "select i.file file,t.url url ,t.id id from  textitems_item i, textitems t where i.fileUrl=t.url and t.sortType='%s' order by i.id desc  limit %s,%s " % (sortType, start, end))
        return self.conn.fetchAll()

    def inertImgChannel(self, obj):
        rate = obj.get("rate", 1.1)
        return self.conn.execute(
            "replace into  imgchannel (name,baseurl,url,updateTime,rate,pic) values ('%s','%s','%s','%s',%s,'%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("updateTime"), rate, obj.get('pic', "")))

    def inertImgItems(self, obj):
        return self.conn.execute(
            "insert into  imgitems (name,baseurl,url,channel,fileDate,pics,updateTime,sortType) values ('%s','%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("fileDate"), obj.get("pics"), obj.get("updateTime"), obj.get("sortType")))

    def inertImgItems_item(self, obj):
        return self.conn.execute(
            "insert into  imgitems_item (picUrl,origUrl,itemUrl) values ('%s','%s','%s')"
            % (obj.get("picUrl"), obj.get("origUrl"), obj.get("itemUrl")))

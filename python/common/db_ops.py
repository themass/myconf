#!/usr/bin/env python
# coding=utf-8
import MySQLdb
import dateutil

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
            "replace into  textitems (name,baseurl,url,channel,fileDate,updateTime,sortType,channelName) values ('%s','%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("fileDate"), obj.get("updateTime"), obj.get("sortType"), obj.get("channelName","")))

    def inertTextItems_item(self, obj):
        return self.conn.execute(
            "replace into  textitems_item (fileUrl,file) values ('%s','%s')"
            % (
                obj.get("fileUrl"), MySQLdb.escape_string(obj.get("file"))))

    def getTextChannel(self):
        self.conn.execute("select * from  textchannel")
        return self.conn.fetchAll()

    def getTextChannelItems(self, channel, i, sortType):
        start = i * 20
        end = (i + 1) * 20
        self.conn.execute(
            "select * from  textitems where channel='%s' and sortType='%s' order by id asc  limit %s,%s " % (channel, sortType, start, end))
        return self.conn.fetchAll()

    def getTextChannelItemsById(self, i, sortType):
        start = i * 80
        end =  80
        print "select i.file file,t.url url ,t.id id from  textitems_item i, textitems t where i.fileUrl=t.url and t.sortType='%s' order by i.id desc  limit %s,%s " % (sortType, start, end)
        self.conn.execute(
            "select i.file file,t.url url ,t.id id from  textitems_item i, textitems t where i.fileUrl=t.url and t.sortType='%s' order by i.id desc  limit %s,%s " % (sortType, start, end))
        return self.conn.fetchAll()

#     def getTextChannelItems(self, i, sortType):
#         start = i * 20
#         end = (i + 1) * 20
#         self.conn.execute(
#             "select i.file file,t.url url ,t.id id from  textitems_item i, textitems t where i.fileUrl=t.url and t.sortType='%s' order by i.id desc  limit %s,%s " % (sortType, start, end))
#         return self.conn.fetchAll()

    def inertImgChannel(self, obj):
        return 1
        return self.conn.execute(
            "replace into  imgchannel (name,baseurl,url,updateTime,rate,pic,showType,channel) values ('%s','%s','%s','%s',%s,'%s',%s,'%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("updateTime"), obj.get("rate"), obj.get('pic', ""), obj.get("showType"), obj.get("channel")))
    def inertImgChannelWithChannel(self, obj,channel):
        return self.conn.execute(
            "replace into  imgchannel (name,baseurl,url,updateTime,rate,pic,showType,channel) values ('%s','%s','%s','%s',%s,'%s',%s,'%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("updateTime"), obj.get("rate"), obj.get('pic', ""), obj.get("showType"), channel))

    def inertImgItems(self, obj):
        return self.conn.execute(
            "replace into  imgitems (name,baseurl,url,channel,fileDate,pics,updateTime,sortType,showType,pic,channelName) values ('%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s','%s')"
            % (
                obj.get("name"), obj.get("baseurl"), obj.get("url"), obj.get("channel"), obj.get("fileDate"), obj.get("pics"), obj.get("updateTime"), obj.get("sortType"), obj.get("showType"), obj.get("pic",''), obj.get("channelName",'')))

    def inertImgItems_item(self, obj):
        return self.conn.execute(
            "insert  ignore  into  imgitems_item (picUrl,origUrl,itemUrl) values ('%s','%s','%s')"
            % (obj.get("picUrl"), obj.get("origUrl"), obj.get("itemUrl")))

    def getImgItems_itemUnSyncById(self, ids):
        sql = "select * from  imgitems_item wher order by id in (%s) "
        in_p = ', '.join(map(lambda x: '%s', ids))
        sql = sql % in_p
        self.conn.execute(sql, ids)
        return self.conn.fetchAll()

    def getImgItems_itemId(self):
        self.conn.execute(
            "select id from  imgitems_item  ")
        objs = self.conn.fetchAll()
        items = []
        for obj in objs:
            items.append(obj['id'])
        return items

    def getImgItems_itemBySortType(self, sortType, channel, start, end):
        sql = "select t.url from imgitems t  where t.channel = '%s' and t.sortType='%s' order by t.id limit %s,%s" % (
            channel, sortType, start, end)
        self.conn.execute(sql)
        ret = self.conn.fetchAll()
        itemUrls = []
        if len(ret) == 0:
            return []
        for item in ret:
            itemUrls.append(item['url'])
        in_p = ', '.join(map(lambda x: '%s', itemUrls))
        sql = "select i.id,i.picUrl,i.itemurl from imgitems_item i where i.itemurl in (%s)"
        sql = sql % in_p

        self.conn.execute(sql, itemUrls)
        return self.conn.fetchAll()

    def updateImgItemsFileUrl(self, itemUrl, imgCdnUrl, imgUrl):
        sql = "update imgitems_item set origUrl=CONCAT('%s',id,'%s'),cdnUrl=CONCAT('%s',id,'%s')" % (
            imgUrl, ".jpg", imgCdnUrl, ".jpg")
        where = " where itemUrl in (%s)"
        in_p = ",".join(map(lambda x: "%s", itemUrl))
        where = where % in_p
        print self.conn.execute(sql + " " + where, itemUrl)

    def updateImgItems_itemSync(self, obj):
        return self.conn.execute(
            "upate  imgitems_item set origUrl='%s',compressUrl='%s' where id=%s"
            % (obj.get("origUrl"), obj.get("compress"), obj.get("id")))
    def deleteVideoItems(self,baseurl):
        self.conn.execute("delete from videoitems_1 where baseurl='%s'"%(baseurl))
    def updateVideoItemsChannelType(self):
        self.conn.execute("update videoitems_1 i set channelType=(select channelType from videochannel c where i.channel=c.channel limit 1)")
    def inertVideoChannel(self, obj):
        try:
            #return 1
            return self.conn.execute(
                "insert into  videochannel_1 (name,url,baseurl,updateTime,rate,showtype,enable,channel,channelType) values ('%s','%s','%s','%s',%s,%s,%s,'%s','%s')"
                % (
                    obj.get("name"), obj.get("url"), obj.get("baseurl"), obj.get("updateTime"), 1.2, obj.get("showType",3), 1, obj.get("channel").replace(".com",'-'), obj.get("channelType")))
        except Exception as e:
            pass
    def renameVideo(self,obj):
        return self.conn.execute(
            "update   videoitems_1 set name='%s' where path='%s'" % ( obj.get("name"), obj.get("path")))
    def inertVideo(self, obj,videoType="normal",baseUrl='',channelType=''):
        sortType = dateutil.y_m_d()
        return self.conn.execute(
            "insert ignore into  videoitems_1 (name,url,channel,pic,updateTime,path,videoType,baseurl,sortType,channelType) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name").replace("'",""), obj.get("url"), obj.get("channel").replace(".com",'-'), obj.get("pic"), obj.get("updateTime"), obj.get("path"), videoType,baseUrl,sortType,channelType))


    def inertVideoUser(self, obj):
        try:
            return 1
            return self.conn.execute(
                "insert ignore into  video_user_1 (name,pic,userId,rate,updateTime,channel,showType,baseurl) values ('%s','%s','%s','%s','%s','%s','%s','%s')"
                % (
                    obj.get("name"), obj.get("pic"), obj.get("userId"), obj.get("rate"), obj.get("updateTime"), obj.get("channel"), obj.get("showType"), obj.get("baseUrl")))
        except Exception as e:
            return 0
    def inertVideoUserItem(self, obj):
        return self.conn.execute(
            "replace into  video_user_item_1 (name,pic,url,userId,rate,updateTime,path,baseurl,videoType,showType) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
            % (
                obj.get("name").replace("'",""), obj.get("pic"), obj.get("url"), obj.get("userId"), obj.get("rate"), obj.get("updateTime"), obj.get("path"), obj.get("baseUrl"), obj.get("videoType"), obj.get("showType")))

    def getAllHost(self):
        self.conn.execute(
            "select * from host_v2 where enable=1 order by com asc,cname desc")
        return self.conn.fetchAll()

    def getAllwannaIplocalnull(self):
        self.conn.execute(
            "select id,ip from iwanna where ip is not null and ip_local is null limit 100")
        return self.conn.fetchAll()

    def updateWannaIpLocal(self, objs):
        for obj in objs:
            self.conn.execute(
                "update iwanna set ip_local = '%s' where id=%s" % (obj['local'], obj['id']))
    def selectDevInfoIpNull(self):
        self.conn.execute(
            "select devId,ip from devuseinfo where ip is not null and loc is null limit 300")
        return self.conn.fetchAll()
    def updateDevinfoLoc(self,objs):
        for item in objs:
            if item.get("loc")!=None:
                return self.conn.execute(
                "update   devuseinfo set loc='%s' where devId='%s'" % ( item.get("loc"), item.get("devId")))
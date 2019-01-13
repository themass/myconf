#!/usr/bin/env python
#coding=utf-8
#Author: Ca0Gu0

from pymongo import MongoClient
import datetime,time



class MongCli(object):
    

    def __init__(self, host="10.200.13.21", port=27118, user='business_adv', passwd ='y7NS@2016#JE2@iKmY', database="adx_materiel"):

        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        
        self.database = database

        client = MongoClient(self.host, self.port)
        client.the_database.authenticate(self.user, self.passwd, source=self.database)
                
        self.db=client[self.database]
        self.posts = self.db.house_agent_relation

    def t(self, args1=None, args2=None):
        
        c=datetime.datetime.now()
        print self.posts.find_one({'house_code':'105101318687'})
        return c
    
    
    
    def write(self,number=100):
        start = self.t(args1="start", args2="write")
        for i in range(number):
            post = {"author": "Mike"+str(i),
                     "text": "My first blog post!"+str(i),
                     "tags": ["mongodb", "python", "pymongo"],
                     "date": datetime.datetime.utcnow()}
            
         
            post_id = self.posts.insert_one(post).inserted_id
        end = self.t(args1="end", args2="write")
        print "Total write runtime: %ss" %str((end-start).seconds)
    
    def read(self):
        start = self.t(args1="start", args2="read")
        output = open("output.txt", 'w')
        for post in self.posts.find():
            try:
                output.write(str(post)+"\n")
            except Exception,e:
                print e
        output.close()
        end = self.t(args1="end", args2="read")
        print "Total read runtime: %ss" %str((end-start).seconds)
        print "----------Split--------"
        
        
if __name__ == "__main__":
    f = MongCli()
    f.read()
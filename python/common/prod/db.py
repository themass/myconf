#!/usr/bin/env python
# coding=utf-8

from common.base.data_base import DataBase
# db_host = '47.88.7.156'
db_host = 'mysql.sspacee.com'
db_port = 6666
db_user = 'vpn@server'
db_passwd = 'Themass@5296'
db_vpn = 'vpn'


class DbVPN(DataBase):

    def __init__(self):
        DataBase.__init__(
            self, host=db_host, port=db_port, user=db_user, passwd=db_passwd, db=db_vpn)

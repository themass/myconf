#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
TODO:通用方法
"""
import datetime,dateutil
import json
import os
import socket
import sys
import traceback
import base64

def base64Decode(src):
    return base64.b64decode(src)


def get_script_name():
    """
    得到命令行中运行脚本的名称（非本模块名）
    """
    file_name = os.path.basename(sys.argv[0])
    if file_name:
        return file_name
    caller = sys._getframe(1)  # Obtain calling frame
    if (caller.f_globals.has_key['__file__']):
        file_path = caller.f_globals['__file__']
        return os.path.basename(file_path)
    else:
        return None


def get_local_ip():
    """
    获取本地ip
    """
    host_name = socket.getfqdn(socket.gethostname())
    return socket.gethostbyname(host_name)


def get_module_dir(f):
    """
    得到python模块的目录，使用方式：在模块代码中调用 get_module_dir(__file__)
    *在apscheduler定时调度的多线程环境下，本文件的__file__有问题，可以通过模块的文件名得到get_module_dir(common.__file__)*
    """
    return os.path.dirname(f)


def ensure_dir(d):
    """
    make dir if not exists
    """
    if not os.path.exists(d):
        os.makedirs(d)

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]
    # 将linux下换行符\n统一换成windows下的\r\n，兼容popo的换行格式
    exception_str = exception_str.replace("\r", "").replace("\n", "\r\n")

    return exception_str


def parse_dbf_time(data_time):
    #dbf时间转换成time对象
    data_time_s = data_time[-14:]
    return dateutil.formattodate(data_time_s, '%Y%m%d%H%M%S')


class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if isinstance(o, datetime.datetime):
                return dateutil.formatdate(o, '%Y/%m/%d %H:%M:%S')
        except TypeError:
            pass
            # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
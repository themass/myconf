#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
logging模块
"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from common.common import get_script_name, format_exception

logging.basicConfig()


class Logger(object):

    def __init__(self, name=None, log_to_file=False, file_name="log.log", rotating=True, console_level=logging.DEBUG,
                 file_level=logging.INFO):
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s', '%Y/%m/%d %H:%M:%S')
        if not name:
            name = get_script_name()
        if name in logging.Logger.manager.loggerDict:
            self.log_obj = logging.getLogger(name)
            return
        log_obj = logging.getLogger(name)
        log_obj.setLevel(logging.DEBUG)

        sh = logging.StreamHandler(sys.stdout)
        # sh = logging.StreamHandler()
        sh.setLevel(console_level)
        sh.setFormatter(formatter)
        log_obj.addHandler(sh)

        if (log_to_file):
            if rotating:
                fh = logging.handlers.TimedRotatingFileHandler(
                    file_name, when='midnight', backupCount=10)
            else:
                fh = logging.FileHandler(file_name)
            fh.setLevel(file_level)
            fh.setFormatter(formatter)
            log_obj.addHandler(fh)

        self.log_obj = log_obj

    def debug(self, msg, *args, **kwargs):
        self.log_obj.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log_obj.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log_obj.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.log_obj.warning(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.log_obj.critical(msg, *args, **kwargs)

    def exception(self, ex):
        self.log_obj.error('%s', format_exception(ex))

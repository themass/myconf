#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
import xlwt


class ExcleWriter(object):
    ctype = 1
    xf = 0  # 扩展的格式化

    def __init__(self):
        object.__init__(self)
        self.index = 0

    def openExcel(self, fileName, sheetName):
        self.fileName = fileName
        self.fileFd = xlwt.Workbook()
        self.sheet = self.fileFd.add_sheet(
            self.__covertStr(sheetName), cell_overwrite_ok=True)

    def writeHead(self, data):
        self.__write(data, self.set_style('Arial', 250, True))

    def writeData(self, data):
        font = self.set_style('Times New Roman', 200, False)
        for obj in data:
            self.__write(obj, font)

    def __write(self, data, sty=None):
        cell = 0
        for item in data:
            try:
                val = self.__covertStr(item)
                self.sheet.write(self.index, cell, val, sty)
            except Exception as e:
                print e
                print item
            cell = cell + 1
        self.index = self.index + 1

    def close(self):
        self.fileFd.save(self.fileName)

    def __covertStr(self, val):
        if isinstance(val, str):
            return unicode(val)
        elif isinstance(val, unicode):
            return val
        else:
            return unicode(str(val))

    def set_style(self, name, height, bold=False):
        style = xlwt.XFStyle()  # 初始化样式

        font = xlwt.Font()  # 为样式创建字体
        font.name = name  # 'Times New Roman'
        font.bold = bold
        font.color_index = 4
        font.height = height

        # borders= xlwt.Borders()
        # borders.left= 6
        # borders.right= 6
        # borders.top= 6
        # borders.bottom= 6

        style.font = font
        # style.borders = borders

        return style

#!/usr/bin/python
# -*-coding:utf-8-*-
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import subprocess
from email.header import Header


def sendEmailShell(fromName, toNames, subject, filepath, files, content):
    fujian = ''
    if len(files) >= 1:
        for fileName in files:
            fujian = fujian + '-a %s' % (os.path.join(filepath, fileName))
    toEmailName = ''
    for name in toNames:
        toEmailName = toEmailName + '%s@lianjia.com;' % (name)
    commond = r'mail -s %s %s  -r "%s" %s' % (
        subject, fujian, fromName, toEmailName)
    ret = subprocess.call(commond, shell=True)


def sendEmail(fromName, toNames, subject, filepath, files, content):
    # 创建一个带附件的实例
    msg = MIMEMultipart()
    attText = MIMEText(content, 'plain', 'utf-8')
    msg.attach(attText)  # 添加邮件正文
    if len(files) >= 1:
        for fileName in files:
            # 构造附件1
            att = MIMEText(
                open(os.path.join(filepath, fileName), 'rb').read(), 'html', 'utf8')
            att["Content-Type"] = 'application/octet-stream'
            name = 'attachment; filename="%s"' % (Header(fileName, 'UTF-8'))
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att["Content-Disposition"] = name
            msg.attach(att)
        # 加邮件头
        toEmail = []
        for name in toNames:
            toEmail.append('%s@lianjia.com' % (name))
        msg['to'] = ';'.join(toEmail)
        msg['from'] = '%s@lianjia.com' % (fromName)
        msg['subject'] = subject
        print toEmail, msg['to']
    # 发送邮件
    try:
        server = smtplib.SMTP()
#         server.set_debuglevel(1)
        server.connect('mail.lianjia.com')
        server.sendmail(msg['from'], toEmail, msg.as_string())
        server.quit()
        print '发送成功'
    except Exception, e:
        print str(e)
if __name__ == '__main__':
    toNames = ['liangmeilun', 'yueli', 'chenfengying01',
               'chenbingwen', 'litiantian', 'liguoqing']
    fileOutpuDir = '/home/work/var/report/excel/'
    files = []
    files.append(u'report_20170719111747.xls')
    files.append(u'report_南京_20170719111747.xls')
    sendEmail('liguoqing', toNames, 'report', fileOutpuDir, files, '测试邮件')

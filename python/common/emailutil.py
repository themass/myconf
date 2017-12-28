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
        toEmailName = toEmailName + '%s@163.com;' % (name)
    commond = r'mail -s %s %s  -r "%s" %s' % (
        subject, fujian, fromName, toEmailName)
    ret = subprocess.call(commond, shell=True)
#
#
# def sendEmail(fromName, toNames, subject, filepath, files, content):
#     # 创建一个带附件的实例
#     msg = MIMEMultipart()
#     attText = MIMEText(content, 'plain', 'utf-8')
#     msg.attach(attText)  # 添加邮件正文
#     if len(files) >= 1:
#         for fileName in files:
#             # 构造附件1
#             att = MIMEText(
#                 open(os.path.join(filepath, fileName), 'rb').read(), 'html', 'utf8')
#             att["Content-Type"] = 'application/octet-stream'
#             name = 'attachment; filename="%s"' % (Header(fileName, 'UTF-8'))
#             # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
#             att["Content-Disposition"] = name
#             msg.attach(att)
#         # 加邮件头
#         toEmail = []
#         for name in toNames:
#             toEmail.append('%s@163.com' % (name))
#         msg['to'] = ';'.join(toEmail)
#         msg['from'] = '%s@163.com' % (fromName)
#         msg['subject'] = subject
#         print toEmail, msg['to']
#     # 发送邮件
#     try:
#         server = smtplib.SMTP()
# #         server.set_debuglevel(1)
#         server.connect('mail.163.com')
#         server.sendmail(msg['from'], toEmail, msg.as_string())
#         server.quit()
#         print '发送成功'
#     except Exception, e:
#         print str(e)

mailto_list = ['liguoqing19861028@163.com']  # 收件人(列表)
mail_host = "smtp.163.com"  # 使用的邮箱的smtp服务器地址，这里是163的smtp地址
mail_user = "liguoqing19861028@163.com"  # 用户名
mail_pass = "163@themass"  # 密码
mail_postfix = "163.com"  # 邮箱的后缀，网易就是163.com


def send_mail(to_list, sub, content):
    me = mail_user
    msg = MIMEText(content, _subtype='plain')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)  # 将收件人列表以‘；’分隔
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)  # 连接服务器
        server.login(mail_user, mail_pass)  # 登录操作
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        print '发送邮件成功'
        return True
    except Exception, e:
        print str(e)
        print '发送邮件失败'
        return False
if __name__ == '__main__':
    #     toNames = ['liangmeilun', 'yueli', 'chenfengying01',
    #                'chenbingwen', 'litiantian', 'liguoqing']
    #     fileOutpuDir = '/home/work/var/report/excel/'
    #     files = []
    #     files.append(u'report_20170719111747.xls')
    #     files.append(u'report_南京_20170719111747.xls')
    send_mail(["liguoqing19861028@163.com"], 'report',  '测试邮件')

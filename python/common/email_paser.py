# -*- coding: utf-8 -*-

import email
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
poplib._MAXLINE = 20480


class MailConn():

    def __init__(self, name, password, pop3Server):
        self.conn(name, password, pop3Server)

    def conn(self, name, password, pop3Server):
        server = poplib.POP3(pop3Server)
        # server.set_debuglevel(1)
        # 认证:
        server.user(name)
        server.pass_(password)
        self.server = server

    def getTitle(self, num=1000, filter=''):
        print('Messages: %s. Size: %s' % self.server.stat())
        resp, mails, octets = self.server.list()
        ret = []
        if len(mails) <= num:
            start = 1
        else:
            start = len(mails) - num
        end = len(mails)
        for i in range(start, end):
            lines = self.server.retr(i)[1]
            # 解析邮件:
            msg = Parser().parsestr('\r\n'.join(lines))
            # 打印邮件内容:
            title = self.get_title(msg)
            if title.count(filter) != 0:
                ret.append(title)
        return ret

    def quit(self):
        # 关闭连接:
        self.server.quit()

    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = self.content_type[pos + 8:].strip()
        return charset

    def decode_str(self, s):
        value, charset = decode_header(s)[0]
#         if charset:
#             value = value.decode(charset)
        print value
        return value

    def get_title(self, msg, indent=0):
        value = msg.get('Subject', '')
        return self.decode_str(value)

    def print_info(self, msg, indent=0):
        if indent == 0:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header == 'Subject':
                        value = self.decode_str(value)
                    else:
                        hdr, addr = parseaddr(value)
                        name = self.decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                print('%s%s: %s' % ('  ' * indent, header, value))
        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                print('%spart %s' % ('  ' * indent, n))
                print('%s--------------------' % ('  ' * indent))
                self.print_info(part, indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                content = msg.get_payload(decode=True)
                charset = self.guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                print('%sText: %s' % ('  ' * indent, content + '...'))
            else:
                print('%sAttachment: %s' % ('  ' * indent, content_type))

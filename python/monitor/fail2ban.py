# -*- coding: utf-8 -*-
from common.email_paser import*

email = 'freevpn_account@163.com'
password = 'themass5296'
pop3_server = 'pop.163.com'
if __name__ == '__main__':
    conn = MailConn(email, password, pop3_server)
    ret = conn.getTitle(10000, "[Fail2Ban] sshd:")

    if len(ret) > 0:
        for obj in ret:
            print obj
    else:
        print '没有恶意攻击'

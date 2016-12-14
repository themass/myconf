# CREATE USER 'radius'@'%' IDENTIFIED BY 'themass';
# GRANT SELECT ON radius.* TO 'radius'@'%';
 GRANT ALL ON radius.* TO 'radius'@'%';
# GRANT ALL on radius.radacct TO 'radius'@'%';
# GRANT ALL on radius.radpostauth TO 'radius'@'%';
 use radius;
 
# 加入组信息，本例中的组名为user
 insert into radgroupreply (groupname,attribute,op,value) values ('vpn_grp','Auth-Type',':=','Local');
 insert into radgroupreply (groupname,attribute,op,value) values ('vpn_grp','Service-Type','=','Framed-User');
 insert into radgroupreply (groupname,attribute,op,value) values ('vpn_grp','Framed-IP-Netmask',':=','255.255.255.0');
 
# 加入用户信息
 INSERT INTO radcheck (UserName, Attribute, Value) VALUES ('vpn', 'Password', 'themass');
 
# 用户加到组里
 insert into radusergroup(username,groupname) values('vpn','vpn_grp');
 
# 限制账户同时登陆次数
 INSERT INTO radgroupcheck (GroupName, Attribute, op, Value) values('vpn_grp', 'Simultaneous-Use', ':=', '1');

#在数据库中限制用户组的最大流量为1M(本例中的用户组名为user)
 INSERT INTO radgroupcheck (GroupName,attribute,op,Value) VALUES ('vpn_grp','Max-Monthly-Traffic',':=','1048576');
  # 流量统计时间的间隔（60秒）
 INSERT INTO radgroupcheck (GroupName,attribute,op,Value) VALUES ('vpn_grp','Acct-Interim-Interval',':=','60');
 # 加入一个新的VPN用户（用户名zhukun.net，密码abc123）
 INSERT INTO radcheck (UserName, Attribute, Value) VALUES ('123', 'Password', '123456');
 #将用户zhukun.net加到组里
 insert into radusergroup(username,groupname) values('123','vpn_grp');
 
 flush privileges; 
 
#select * from information_schema.user_privileges;
#update user set password=password('themass') where user='root';
#drop user 'radius'@'%';
#show grants for 'radius'@'%';
#删除空用户名的记录
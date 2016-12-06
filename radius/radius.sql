 GRANT SELECT ON radius.* TO 'radius'@'localhost' IDENTIFIED BY 'themass';
 GRANT ALL on radius.radacct TO 'radius'@'localhost';
 GRANT ALL on radius.radpostauth TO 'radius'@'localhost';
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
 INSERT INTO radgroupcheck (GroupName, Attribute, op, Value) values("vpn_grp", "Simultaneous-Use", ":=", "1");

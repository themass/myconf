CREATE USER 'radius'@'%' IDENTIFIED BY 'Themass@5296';
CREATE USER 'vpn@server'@'%' IDENTIFIED BY 'Themass@5296';
GRANT ALL ON radius.* TO 'vpn@server'@'%';
GRANT ALL ON vpn.* TO 'vpn@server'@'%';
GRANT SELECT,INSERT,UPDATE,DELETE ON radius.* TO 'radius'@'%';

flush privileges; 
 
#select * from information_schema.user_privileges;
#update user set password=password('themass') where user='root';
#drop user 'radius'@'%';
#show grants for 'radius'@'%';
#删除空用户名的记录
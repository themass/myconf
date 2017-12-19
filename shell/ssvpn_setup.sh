PANEL_WORKDIR=/home/web/webroot
PANEL_TMP_HOME=/home/web/soft

PANEL_SHELL_HOME=/home/web/work/myconf/shell


WORKDIR=/home/web/webroot
TMP_HOME=/root/soft

#https://doub.io/ss-jc13/
setup_sspanel() 
{
	cd ${PANEL_TMP_HOME}
	wget https://github.com/orvice/ss-panel/archive/v2.zip
	unzip v2.zip
	mv ss-panel-v2  ${PANEL_WORKDIR}/ss-panel
	cp ${PANEL_SHELL_HOME}/../php/config.php ${PANEL_WORKDIR}/ss-panel/lib
	mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/invite_code.sql
	mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/ss_node.sql
	mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/ss_reset_pwd.sql
	mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/ss_user_admin.sql
	mysql -u vpn@server -p -hmysql.sspacee.com vpn < ${PANEL_WORKDIR}/ss-panel/user.sql
	echo 'http://hostggg.com/pwd.php?pwd=1993'
}

## -----------------------
## Show help message
## -----------------------
usage() 
{
    echo "Available arguments as below:"
    echo "soft           Setup init soft"
    echo "strongswan          Setup strongswan"
    echo "strongswanconf          Setup strongswan config"
    echo "ca           Setup ca"
    echo "iptables         Setup iptables"
    echo "net    Setup net"
    echo "fail2ban    Setup fail2ban"
    echo "check    checkspeed"
     echo "check_vpn    check vpn"
     echo "net    Setup net"
    echo "all           Setup all aboves"
}

## =====================================
## The main process
## =====================================
if [ $# != 0 ]; then
    for arg in $*; do
        case "$arg" in
            soft)            init_soft;;
            strongswan)          strongswan_setup;;
	    ca)          init_ca $2;;
	    iptables)          setup_iptables;;
	    strongswanconf)          strongswan_config;;
	    net)          net;;
	     fail2ban)          setup_fail2ban;;
	    check)          checkspeed;;
	    check_vpn)          check_vpn;;
	    all)          setup_all;;
        esac
    done
else
    usage
fi

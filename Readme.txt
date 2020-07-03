useradd -r -m -s /bin/bash web
chmod 777 /etc/sudoers
 echo 'web  ALL=(ALL)    ALL' >> /etc/sudoers  
chmod 440 /etc/sudoers
passwd web 
ap

mkdir -p /home/web/install
cd /home/web/install 
wget https://ftp.gnu.org/gnu/gmp/gmp-6.0.0a.tar.bz2 --no-check-certificate
tar -xvjpf gmp-6.0.0a.tar.bz2
cd gmp-6.0.0
./configure 
make 
make check
sudo make install


cd /home/web/install 
wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tar.xz
xz -d Python-2.7.10.tar.xz
tar -xvf Python-2.7.10.tar
cd Python-2.7.10
./configure --prefix=/home/web/local/python2.7.10/
make && make install

cd /home/web/local/
rm python2.7
ln -s python2.7.10 python2.7



echo 'export PYTHONE_HOME=/home/web/local/python2.7' >> ~/.bash_profile
echo 'export PATH=$PYTHONE_HOME/bin:/$PATH'  >> ~/.bash_profile
echo 'export PYTHONPATH=/home/web/work/myconf/python'  >> ~/.bash_profile
source ~/.bash_profile


echo 'export PYTHONE_HOME=/home/web/local/python2.7' >> ~/.profile
echo 'export PATH=$PYTHONE_HOME/bin:/$PATH'  >> ~/.profile
echo 'export PYTHONPATH=/home/web/work/myconf/python'  >> ~/.profile
source ~/.profile


cd /home/web/install
wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate
python get-pip.py
pip install -U pip setuptools
cd /home/web/local/python2.7/bin
pip install python-memcached
pip install pymongo
pip install redis
pip install apscheduler
pip install xlwt
pip install xlrd
pip install BeautifulSoup
pip install requests
pip install pycrypto
pip install selenium
#pip install MySQL-python
# MySQLdb
cd /home/web/install
wget https://pypi.python.org/packages/a5/e9/51b544da85a36a68debe7a7091f068d802fc515a3a202652828c73453cad/MySQL-python-1.2.5.zip#md5=654f75b302db6ed8dc5a898c625e030c  --no-check-certificate
unzip MySQL-python-1.2.5.zip
cd MySQL-python-1.2.5
python setup.py  install
#  失败请看	 http://www.cnblogs.com/bincoding/p/6480884.html
# sudo apt-get install mysql-server mysql-client 
#http://asdf314159265.iteye.com/blog/1841963
#http://blog.csdn.net/it_dream_er/article/details/50760020
#sudo ln -s /home/web/install/mysql-5.6.10-linux-glibc2.5-x86_64/lib/libmysqlclient.so /usr/lib/libmysqlclient.so.18
#windows  http://www.mamicode.com/info-detail-2206925.html
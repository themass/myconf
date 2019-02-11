import sys
import os
import time
import socket
import random
#Code Time
from datetime import datetime
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 绑定 客户端口和地址:
s.bind(('0.0.0.0', 3000))
print 'Bind UDP on 9999...'
while True:
    # 接收数据 自动阻塞 等待客户端请求:
    data, addr = s.recvfrom(1024)
    print 'Received from %s:%s.' % addr
    s.sendto('Hello, %s!' % data, addr)
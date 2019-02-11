import sys
import os
import time
import socket
import random
from datetime import datetime
sys.setdefaultencoding('utf8')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 3000))
print 'Bind UDP on 9999...'
while True:
    data, addr = s.recvfrom(1024)
    print 'Received from %s:%s.' % addr
    s.sendto('Hello, %s!' % data, addr)
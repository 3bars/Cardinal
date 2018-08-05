#!/usr/bin/python

import paramiko
import time
import sys

queryIP = sys.argv[1]
queryUser = sys.argv[2]
queryPass = sys.argv[3]
queryTFTP = sys.argv[4]
queryTFTPName = sys.argv[5]

ip = queryIP
username = queryUser
password = queryPass
tftp = queryTFTP
tftpname = queryTFTPName

remote_conn_pre=paramiko.SSHClient()
remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
remote_conn_pre.connect(ip, port=22, username=username,
                        password=password,
                        look_for_keys=False, allow_agent=False)

remote_conn = remote_conn_pre.invoke_shell()
output = remote_conn.recv(65535)


remote_conn.send("enable\n")
time.sleep(.10)
output = remote_conn.recv(65535)


remote_conn.send('%s\n' % password)
time.sleep(.15)
output = remote_conn.recv(65535)


remote_conn.send("copy running-config tftp\n")
time.sleep(.15)
output = remote_conn.recv(65535)


remote_conn.send('%s\n' % tftp)
time.sleep(.15)
output = remote_conn.recv(65535)


remote_conn.send('%s\n' % tftpname)
time.sleep(.15)
output = remote_conn.recv(65535)


exit()


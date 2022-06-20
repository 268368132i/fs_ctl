#!/usr/bin/python

import socket
import os, os.path
import time
import ESL
from collections import deque
from time import sleep

if os.path.exists("/tmp/socket_test.s"):
  os.remove("/tmp/socket_test.s")

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind("/tmp/socket_test.s")

while True:
  try:
    host = 'localhost'
    port=8021
    password = 'ClueCon'
    print("Connecting to ESL at {0}:{1}".format(host,port))
    eslcon = ESL.ESLconnection(host, port, password)

    while eslcon.connected():
      server.listen(1)
      conn, addr = server.accept()
      datagram = conn.recv(1024)
      if datagram:
        print('data {!r}'.format(datagram))
        resp = eslcon.sendRecv('api ' + datagram).getBody()
        print(resp)
        conn.sendall(resp)
        conn.close()
  except AttributeError as e:    
    print "AttributeError"
    
  wait=2
  print "Waiting {0} seconds before reconnect".format(wait)
  sleep(wait)

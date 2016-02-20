#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
from Socket import Socket

server_name = "localhost"
server_port = 2080
message = "hello"

def main():
	with Socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
		client_socket.connect((server_name, server_port))
		client_socket.send(message)
		reply = client_socket.recv(1024)
		# print reply

	return 0


if __name__ == '__main__':
	sys.exit(main())
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function    # to use the syntax about print of python3


import argparse

import sys
import time
import socket
from socket import socket as Socket


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--server-port', '-p', default=2081, type=int,
						help='Server_Port to use')

	parser.add_argument('--run-server', '-r', action='store_true',
						help='Run a ping server')

	parser.add_argument('server_address', default='localhost',
						help='Server to ping, no effect if running as a server')

	args = parser.parse_args()

	if args.run_server:
		return run_server(args.server_port)
	else:
		return run_client(args.server_address, args.server_port)


def run_server(server_port):
	# Run UDP pinger server

	try:
		server_socket = Socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		server_socket.bind(('', server_port))

		print("Ping server ready on port", server_port)
		while True:
			_, client_address = server_socket.recvfrom(1024)
			server_socket.sendto("".encode(), client_address)
	finally:
		server_socket.close()

	return 0


def run_client(server_address, server_port):
	# Ping a UDP pinger server running at the given address
	
	try:
		client_socket = Socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Time out after 1 second
		client_socket.settimeout(1.0)

		print("Pinging", str(server_address), "on port", server_port)

		for i in range(10):
			client_socket.sendto("".encode(), (server_address, server_port))

			try:
				time_start = time.time()
				_, _ = client_socket.recvfrom(1024)
				time_stop = time.time()
			except socket.timeout:
				print("Packet lost")
			else:
				print("RTT(Round trip time): {:.3f}ms".format((time_stop - time_start) * 1000))
	finally:
		client_socket.close()

	return 0


if __name__ == '__main__':
	sys.exit(main())
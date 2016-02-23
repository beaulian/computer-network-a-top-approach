#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import sys
import socket
import itertools
from socket import socket as Socket

from threading import *

BUFFER_SIZE = 4096
REMOTE_PORT = 80


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--port', '-p', default=8080, type=int,
	                    help='Port to use')
	args = parser.parse_args()

	try:
	    server_socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
	    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)

	    server_socket.bind(('', args.port))
	    server_socket.listen(1)

	    cache_dict = {}

	    print "Proxy server ready..."

	    while True:
	    	try:
	    		connection_socket = server_socket.accept()[0]

	    		t = Thread(target=handle_http, args=[cache_dict, connection_socket])
	    		t.setDaemon(1)
	    		t.start()
	    		t.join()
	    	except socket.error, e:
	    		print e
	    	finally:
	    		connection_socket.close()
	    	
	finally:
		server_socket.close()

	return 0


def handle_http(cache_dict, connection_socket):
	print "new child ", currentThread().getName()

	request_string = connection_socket.recv(BUFFER_SIZE).decode().replace("\r\n", "\n")
	http_dict = http_parse(request_string)
	full_url = http_dict["Host"] + http_dict["Uri"] if "http" not in http_dict["Uri"] else http_dict["Uri"]

	# check cache for page
	cached_page = cache_dict.get(full_url)

	if cached_page is None:
		cached_page = get_page(http_dict["Host"], request_string).replace("\r\n", "\n").encode("utf-8")
		cache_dict[full_url] = cached_page

		print "Serving page ", full_url, " and cached it"
		print "\n"
		print cached_page
	else:
		print "Got page from ", full_url, " from cache"

	connection_socket.send(cached_page)
	connection_socket.close()


def http_parse(request_string):
	try:
		header, body = request_string.split("\n\n")
	except ValueError:
		header = request_string
		body = None

	header_lines = header.rstrip().split("\n")
	method, uri, version = header_lines[0].split()
	headers = [l.split(': ') for l in header_lines[1:]]
	return dict(itertools.chain(
			[('Method', method), ('Uri', uri), ('Version', version)],
			headers, [('Body', body)]
		))


def get_page(server_address, request_string):
	try:
		client_socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_address, REMOTE_PORT))

		client_socket.send(request_string.encode())

		reply = bytes()
		while True:
			part_body = client_socket.recv(BUFFER_SIZE).decode("utf-8", "ignore")
			# print part_body
			if not len(part_body):
				break
			reply += part_body

	finally:
		client_socket.close()

	return reply


def http_format_request(request_dict): 
    return "GET {1} HTTP/1.1\nHost: {2}".format(request_dict['Uri'], request_dict['Host'])


if __name__ == '__main__':
	sys.exit(main())
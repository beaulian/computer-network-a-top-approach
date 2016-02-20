#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import os
import sys
import itertools
import socket
from socket import socket as Socket

base_dir = os.popen('pwd').read().rstrip('\n')


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--port', '-p', default=2080, type=int,
						help='Port to use')
	args = parser.parse_args()

	"""Create the server socket (to handle tcp requests using ipv4), make sure
	it is always closed by using with statement.
	"""
	try:
		server_socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		server_socket.bind(('', args.port))
		server_socket.listen(1)

		print "server ready..."

		while True:
			try:
				connection_socket = server_socket.accept()[0]
				request = connection_socket.recv(1024).decode('ascii')
				reply = http_handle(request)
				connection_socket.send(reply.encode('ascii'))


				print "\n\nReceived request"
				print "======================"
				print request.rstrip()
				print "======================"

				print "\n\nReplied with"
				print "======================"
				print reply.rstrip()
				print "======================"
			finally:
				connection_socket.close()
	finally:
		server_socket.close()


	return 0


def http_handle(request_string):
	"""Given a http request return a response

	Both request and response are unicode strings with platform standard
	line endings.
	"""

	assert not isinstance(request_string, bytes)

	# raise NotImplementedError

	request = http_parse(request_string)

	assert request["Method"] == "GET"
	assert request["Version"] == "HTTP/1.1"

	file_path = base_dir + request['Uri']

	try:
		with open(file_path) as f:
			status = 200
			body = f.read()
	except IOError:
		status = 404
		body = 'File Not Found'
	except UnicodeDecodeError:
		status = 400
		body = 'Cannot handle binary files'

	return make_response({
			'Version': 'HTTP/1.1',
			'Status': status,
			'Content-Type': 'text/plain',
			'Body': body
		})


def http_parse(request_string):
	try:
		header, body = request_string.split("\n\n")
	except ValueError:
		header = request_string
		body = None

	header_lines = header.rstrip().split("\n")
	print request_string
	method, uri, version = header_lines[0].split()
	headers = [l.split(': ') for l in header_lines[1:]]
	return dict(itertools.chain(
			[('Method', method), ('Uri', uri), ('Version', version)],
			headers, [('Body', body)]
		))


def make_response(message):
	phrases = {
		200: 'OK',
		404: 'Not Found',
		400: 'Bad Request'
	}

	status_line = "{0} {1} {2}".format(
		message['Version'], message['Status'], phrases[message['Status']]		
	)
	header_lines = '\n'.join(['{0}: {1}'.format(k, v)
							  for k,v in message.items()
							  if k not in ['Version', 'Status', 'Body']])
	return ''.join([status_line, header_lines,
					'\n\n', message['Body'], '\n'])


if __name__ == '__main__':
	sys.exit(main())

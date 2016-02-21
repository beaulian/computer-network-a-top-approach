#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import sys
import socket
from socket import socket as Socket


"""How to run this program?
    -> First, you should install a mail server(called Mail Transfer Agent)
       like postfix or sendmail, I recommend the postfix, 
       then run the command:
       'python mail-client.py <your hostname>@localhost localhost <mail_address> <message>' 
"""


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("sender_address", type=str)
	parser.add_argument("mail_server", type=str)
	parser.add_argument("receiver_address", type=str)
	parser.add_argument("message", type=str)
	args = parser.parse_args()

	send_mail(args.sender_address, args.mail_server, args.receiver_address, args.message)

	return 0


def send_mail(sender_address, mail_server, receiver_address, message):
	try:
		client_socket = Socket(socket.AF_INET, socket.SOCK_STREAM)

		# set a 1 second timeout
		client_socket.settimeout(1.0)

		# connect to mail server
		client_socket.connect((mail_server, 25))

		def send(string):
			"""Helper function: fix newlines, encode and send a string"""
			final = string.replace("\n", "\r\n").encode("ascii")
			print "Sending " + final + "..."
			client_socket.send(final)

			return 0

		def recv_and_check(expected=250):
			"""Helper function: recive reply and check it's ok"""
			reply = client_socket.recv(2048)
			print "Got: ", reply

			code = int(reply.rstrip().split()[0])
			if code != expected:
				raise Exception(reply)

			return 0

		# get initial message from server
		recv_and_check(220)

		# send greeting
		send("HELO {}\n".format(sender_address.split("@")[1]))
		recv_and_check()

		# set sender address
		send("MAIL FROM: {}\n".format(sender_address))
		recv_and_check()

		# set receiver address
		send("RCPT TO: {}\n".format(receiver_address))
		recv_and_check()

		# prepare to send message
		send("DATA\n")
		recv_and_check(354)

		# send the message itself followed by terminator
		send("{}\n.\n".format(message))
		recv_and_check()

		send("QUIT\n")
		recv_and_check(221)

	finally:
		client_socket.close()


	return 0


if __name__ == '__main__':
	sys.exit(main())
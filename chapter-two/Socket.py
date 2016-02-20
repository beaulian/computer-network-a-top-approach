#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""create a context manager to suport with-statement
   writed by gavin Guan
   2016-02-20
"""

from socket import socket


class Socket(socket):

	def __init__(self, ip_type, pro_type):
		self.ip_type = ip_type
		self.pro_type = pro_type
		super(Socket, self).__init__(ip_type, pro_type)

	def Accept(self):
		import new
		c,a = self.accept()
		setattr(c.__class__, '__exit__', new.instancemethod(self.__exit__, None, c.__class__))
		setattr(c.__class__, '__enter__', new.instancemethod(self.__enter__, None, c.__class__))
		return c,a

	def __enter__(self, *args):
	    return self.__class__(self.ip_type, self.pro_type)

	def __exit__(self, *args):
		self.close()
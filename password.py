#!/usr/bin/env python3
import hashlib
import os


class main():

	def hash_password(self, password):
		passw = password.encode()
		# salt = os.urandom(64)
		salt = b'hello'
		h = hashlib.scrypt(passw, salt=salt, n=2048, r=8, p=1, dklen=32).hex()
		return h
	
	def __init__(self, password):
		passw = password.encode()
		# salt = os.urandom(64)
		salt = b'hello'
		self.password = hashlib.scrypt(passw, salt=salt, n=2048, r=8, p=1, dklen=32).hex()


	def __repr__(self):
		return f'{self.password!r}'



if __name__ == '__main__':
	password = "hello"
	yicks = "hello"
	m = main(password)
	print(m)
	print(type(m))
	y = m.hash_password(yicks)
	print(y)
	print(type(y))
	if m == y:
		print('Y')
	else:
		print('N')

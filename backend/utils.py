from flask import jsonify
from tokens import Token
import binascii
import os

class Utils():
	DEFAULT_ENTROPY = 128
	@staticmethod
	def make_response(data, status_code):
		response = jsonify(data);
		response.status_code = status_code;
		return response

	@staticmethod
	def get_token(cookie):
		token = Token.decode(cookie);
		if Token.is_valid(token):
			return token;
		return None

	@staticmethod
	def token_hex(nbytes=None):
		if nbytes is None:
			nbytes = Utils.DEFAULT_ENTROPY
		random_bytes = os.urandom(nbytes)
		return binascii.hexlify(random_bytes).decode('ascii')
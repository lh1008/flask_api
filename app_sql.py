#!/usr/bin/env python3
from flask import Flask, jsonify, request, session, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, select
from sqlalchemy import Column, insert, Table, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
import hashlib 
import os
import secrets
import jwt



app = Flask(__name__)
engine =  create_engine('postgresql://postgres:newPassword@localhost:5434/sqlalchemy_db')
secret = secrets.token_hex()
app.secret_key =  secret

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	client_id =  Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	name = Column(String(30), nullable=False)
	email = Column(String(50), nullable=False, unique=True)
	password = Column(String(), nullable=False)

	def __init__(self, name, email, password):
		self.name = name
		self.email = email
		passw = password.encode()
		salt = b'hello'
		self.password = hashlib.scrypt(passw, salt=salt, n=2048, r=8, p=1, dklen=32).hex()

	def __repr__(self):
		return f'User(client_id={self.client_id!r}, name={self.name!r}, email={self.email!r}, password={self.password!r})'

def hash_password(password):
	# Method to hash/encrypt a text
	passw = password.encode()
	salt = b'hello'
	h = hashlib.scrypt(passw, salt=salt, n=2048, r=8, p=1, dklen=32).hex()
	return h

def verify_token(token, client_id):
	# Method to verify a sent token to route /users
	header = jwt.get_unverified_header(token)
	t = jwt.decode(token, key=app.secret_key, algorithms=[header['alg']])
	if t['client_id'] == client_id:
		return True
	else:
		return False
		

@app.route('/')
def index():
        return 'Index'


@app.route('/users/', methods=['POST'])
def create_user():
	# Route that will create a user given a set of data
	with Session(engine) as session:
		
		forms = request.form 
		name = forms.get('name')
		email = forms.get('email')
		password = forms.get("password")

		sql = User(name=f"{name}", email=f"{email}", password=f"{password}")
		session.add(sql)
		session.commit()
		return 'User created'


@app.route('/users', methods=['GET'])
def get_users():
	# Route to list users with a validated token
	if request.headers.get('Authorization'):
		auth = request.headers['Authorization']
		client_id = request.headers['client_id']
		if verify_token(auth, client_id) is True:
			with Session(engine) as session:
				query = select([User.client_id, User.name, User.email, User.password])
				res = session.execute(query)
				output = list()

				for row in res:
					output.append(dict(row))
				return jsonify(output)
		else:
			response_object = {
			"status": "Wrong token!"
		}
		return response_object
	else:
		response_object = {
			"status": "Not Authorized"
		}
		return response_object


@app.route('/login', methods=['GET', 'POST'])
def login():
	# Route to log in a user 
	with Session(engine) as session:

		forms = request.form
		email = forms.get('email')
		passw = forms.get('password')
		m = hash_password(passw)
		
		result = session.execute(select(User.client_id, User.name, User.email, User.password).where(User.email == f'{email}'))
		for client_id, name, email, password in result:
			if m == password:
				client_id = f'{client_id}'
				payload_data = {
				"client_id": f'{client_id}',
				"name": f'{name}'
				}
				secret = app.secret_key
				token = jwt.encode(
					payload = payload_data,
					key = secret
					)
				return token + " " + client_id
			else:
				response_object = {
					'status': False,
					'message': 'Wrong Password!'
					}
				return response_object


if __name__ == '__main__':


	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)

# Create user and login

# curl -d "name=Leo&email=leo@insert.com&password=hello" -X POST http://127.0.0.1:5000/users
# curl -d "name=Leo&email=leos@insert.com&password=bear" -X POST http://127.0.0.1:5000/users
# login curl -d "email=leo@insert.com&password=hello" -X POST http://127.0.0.1:5000/login
# login curl -d "email=leos@insert.com&password=bear" -X POST http://127.0.0.1:5000/login

# curl -d "name=Nicolas&email=nico@insert.com&password=hello" -X POST http://127.0.0.1:5000/users
# login curl -d "email=nico@insert.com&password=hello" -X POST http://127.0.0.1:5000/login

# curl -d "name=Luis&email=luis@insert.com&password=yellow" -X POST http://127.0.0.1:5000/users
# login curl -d "email=luis@insert.com&password=yellow" -X POST http://127.0.0.1:5000/login

# Authorization Header
#curl -H "Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjbGllbnRfaWQiOiI2N2M0ZWU5ZC1kNmE4LTQyNmYtOTc2MS1jMTNiOGU4Y2EyZDQiLCJuYW1lIjoiTGVvIn0.PFO2fzv3iUaCtc_1wCpU4ICe6_xmVEsc397yacbWwwE" \
#     -H "client_id: 67c4ee9d-d6a8-426f-9761-c13b8e8ca2d4" \
#    http://127.0.0.1:5000/users
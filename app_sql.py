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
	passw = password.encode()
	salt = b'hello'
	h = hashlib.scrypt(passw, salt=salt, n=2048, r=8, p=1, dklen=32).hex()
	return h

def verify_token(token, client_id):
	headers = jwt.get_unverified_header(token)
	t = jwt.decode(token, key=app.secret_key, algorithms=[headers['alg']])
	if t['client_id'] == client_id:
		return True
	else:
		return False
		

@app.route('/')
def index():
        return 'Index'


@app.route('/users', methods=['POST'])
def create_user():
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
    with Session(engine) as session:
        query = select([User.client_id, User.name, User.email, User.password])
        res = session.execute(query)
        output = list()

        for row in res:
            output.append(dict(row))

        r = select(User).where(User.name == 'Leo')
        rec = session.execute(r)
        for user_object in rec.scalars():
        	print(f'{user_object.name}')
    return jsonify(output)


@app.route('/login', methods=['GET', 'POST'])
def login():
	with Session(engine) as session:

		forms = request.form
		email = forms.get('email')
		passw = forms.get('password')
		m = hash_password(passw)
		
		result = session.execute(select(User.client_id, User.name, User.email, User.password).where(User.email == f'{email}'))
		for u in result:
			if m == u.password:
				client_id = f'{u.client_id}'
				print(client_id)
				payload_data = {
				"client_id": f'{u.client_id}',
				"name": f'{u.name}'
				}
				secret = app.secret_key
				token = jwt.encode(
					payload = payload_data,
					key = secret
					)
				response_object = {
					'status': True,
					'message': 'Successful login',
					'token': verify_token(token, client_id)
				}
				return response_object
			else:
				response_object = {
					'status': False,
					'message': 'Wrong Password!'
					}
				return response_object


if __name__ == '__main__':


	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)


# curl -d "name=Leo&email=leo@insert.com&password=hello" -X POST http://127.0.0.1:5000/users
# login curl -d "email=leo@insert.com&password=hello" -X POST http://127.0.0.1:5000/login

# curl -d "name=Luis&email=luis@insert.com&password=yellow" -X POST http://127.0.0.1:5000/users
# login curl -d "email=luis@insert.com&password=yellow" -X POST http://127.0.0.1:5000/login
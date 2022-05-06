from flask import Flask, request
from flask_restful import Resource, Api
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text


app = Flask(__name__)
engine =  create_engine('postgresql://postgres:newPassword@localhost:5434/flask_db')

@app.route('/')
def index():
        return 'Index'

@app.route('/users', methods=['POST'])
def create_user():
    with engine.connect() as conn:

        forms = request.form 
        name = forms.get("name")
        email = forms.get("email")

        print(name)

        sql = text("INSERT INTO users (name, email) VALUES (:name, :email)")
        val = [{"name": f"{name}", "email": f"{email}"}]
        conn.execute(sql, val)
    return 'User created'

@app.route('/users', methods=['GET'])
def get_users():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM users"))
        output = list()

        for row in res:
            output.append(dict(row))

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)

    # conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
    #  conn.execute(
    #     text("CREATE TABLE IF NOT EXISTS users (client_id uuid DEFAULT uuid_generate_v4(), name char(25), email VARCHAR NOT NULL)")
    # )

# res = conn.execute(text("SELECT * FROM users"))
# for row in res:
#          print(f"client_id: {row.client_id} name: {row.name} email: {row.email}")
# how to send parameters to a POST request


    #conn.execute(
    #        text("INSERT INTO users (name, email) VALUES (:name, :email)"),
    #        [{"name": "Other", "email": "other@insert.com"}]
    #    )

# curl -d "name=Leo&email=leo@insert.com" -X POST http://127.0.0.1:5000/users
# curl -d '{"name": "Jake"}' -d '{"email": "jake@insert.com"}' -X POST http://127.0.0.1:5000/users
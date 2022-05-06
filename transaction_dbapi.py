from flask import Flask
from flask import request
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import text
from sqlalchemy.orm import registry
from sqlalchemy.orm import relationship
import uuid


app = Flask(__name__)

engine =  create_engine('postgresql://postgres:newPassword@localhost:5434/flask_db')

mapper_registry = registry()
Base = mapper_registry.generate_base()
client_id = str(uuid.uuid4())

@app.route('/users/client_id', method=POST)
def index(self):
    with engine.connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
        conn.execute(
            text("CREATE TABLE IF NOT EXISTS users (client_id uuid DEFAULT uuid_generate_v4(), name char(25), email VARCHAR NOT NULL)")
        )
        conn.execute(
            text("INSERT INTO users (name, email) VALUES (:name, :email)"),
            [{"name": f"{self.name}", "email": "lherrera@addi.com"}, {"name": "Maria", "email": "maria@addi.com"}]
        )
        res = conn.execute(text("SELECT * FROM users"))
        for row in res:
            print(f"client_id: {row.client_id} name: {row.name} email: {row.email}")
        print(result.all())
    return 'Index'

class User(Base):
    __tablename__ = 'users'

    client_id = Column(client_id, primary_key=True)
    name = Column(String(25))
    email = Column(String, nullable=False)

    def __repr__(self):
        return f"User(client_id={self.id!r}, name={self.name!r}, email={self.email!r})"

if __name__ == '__main__':
    app.run(debug=True)

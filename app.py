import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object('config.Config')

db = SQLAlchemy(app)

from routes import *  # Import your route definitions


def create_database():
    if not os.path.exists('data.db'):
        with app.app_context():  # Create an app context before using db.create_all()
            db.create_all()
            print("Database and tables created!")
    else:
        print("Database already exists, skipping creation.")




if __name__ == "__main__":
    create_database()
    app.run(debug=True)

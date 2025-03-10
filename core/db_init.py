# db_init.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Get absolute path to the project directory
basedir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(basedir, 'messages.db')

# Create a minimal app just for database setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Using database at: {dbpath}")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define your model directly in this file for initialization
class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.String(36), primary_key=True)
    encrypted_content = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(24), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    max_views = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)

# Create the tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
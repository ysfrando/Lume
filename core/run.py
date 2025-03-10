# run.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask
from app.database import db
from app.api import app as api_blueprint

# Get absolute path to the project directory
basedir = os.path.abspath(os.path.dirname(__file__))
dbpath = os.path.join(basedir, 'messages.db')

def create_app():
    app = Flask(__name__, 
                static_folder='app/static', 
                template_folder='app/templates')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbpath}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    app.register_blueprint(api_blueprint)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
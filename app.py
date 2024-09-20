from flask import Flask, render_template 
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__) # is running the flask web server

import config

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login' 

import models

import routes

if __name__ == '__main__':
    app.run(debug=True) # debug=True will show the errors in the browser also 
    

# app.app_context().push() # will allow for direct access to app via other models (for db and authentication)
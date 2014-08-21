from flask import Flask
from flask.ext.mail import Mail
app = Flask(__name__)
mail = Mail(app)
from loghub import modules
from loghub.routes import users
from loghub.routes import alarms
from loghub.routes import applications
from loghub.routes import logs
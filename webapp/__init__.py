from os import path
import pathlib

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from webapp.appconfig import AppConfig


app = Flask(__name__)
app.config["SECRET_KEY"] = "this should be my secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

APP_PATH = str(pathlib.Path(__file__).parent.absolute())
config = AppConfig(APP_PATH + "/config.yaml")
app_config = config.get_full_config()

db = SQLAlchemy(app)

APP_TITLE = app_config["Application"]["Title"]
APP_VERSION = app_config["Application"]["Version"]

from webapp import routes
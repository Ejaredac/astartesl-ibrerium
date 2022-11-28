from flask import Flask, request, jsonify,session
from flask_session import Session
from flask_cors import CORS
from database import db
from encript import bcrypt
from flask_migrate import Migrate
from config import BaseConfig
from models import User
from sqlalchemy import exc
from functools import wraps
from routes.user.user import appuser
from routes.images.images import imageUser
from routes.libros.libros import applibros
from flask_bootstrap import Bootstrap
from flask import render_template

app = Flask(__name__)
app.register_blueprint(appuser)
app.register_blueprint(imageUser)
app.register_blueprint(applibros)
app.config.from_object(BaseConfig)
CORS(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt.init_app(app)
db.init_app(app)
migrate = Migrate(app)
migrate.init_app(app, db)
bootstrap = Bootstrap(app)

@app.route('/')
@app.route('/inicio')
def inicio():
    user=""
    return render_template('index.html', user = user)


@app.errorhandler(404)
def paginaNoEncontrada(error):
    return render_template('404.html',error=error) , 404
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config.py')
from application import route
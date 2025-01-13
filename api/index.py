from flask import Flask
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    message = {"status": "OK"}
    return json.dumps(message)

@app.route('/about')
def about():
    return 'About'
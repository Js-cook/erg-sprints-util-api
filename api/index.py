from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def home():
    message = {"status": "OK"}
    return json.dumps(message)

@app.route('/about')
def about():
    return 'About'
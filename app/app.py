from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Flask"

@app.route("/hello/<name>")
def hello_there(name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"Hello {name}. It's {now}"
    
    return content
    
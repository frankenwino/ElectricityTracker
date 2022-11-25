from flask import Flask
from datetime import datetime
from flask import render_template
import database
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electricity.db'

@app.route("/")
def home():
    return "Hello Flask"

@app.route("/hello/<name>")
def hello_there(name=None):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"Hello {name}. It's {now}"
    
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )


@app.route("/intradaytest")
def intraday():
    # lpd = database.latest_price_data()
    
    r1 = (1, "Andrew", "Browne", "2.2")
    r2 = (2, "Alex", "Ripa", "1.1")
    r3 = (3, "Bruce", "Lee", "0.5")
    
    l = [r1, r2, r3]
    
    return render_template("intraday.html", table_data=l, table_title="Intraday Prices")
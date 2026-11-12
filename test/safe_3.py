from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/greet")
def greet():
    name = escape(request.args.get("name", ""))
    return f"<h1>Xin chao {name}</h1>"
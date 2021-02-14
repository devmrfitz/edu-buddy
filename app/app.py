from flask import Flask, render_template, request
import app.intermediate

app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return "hello"


if __name__ == "__main__":
    app.run()

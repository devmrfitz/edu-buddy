import flask
from app.bot_brain import reply
api = flask.Blueprint('api', __name__)

@api.route("/get", methods=['GET', 'POST'])
def api_get():
    if flask.request.method == 'GET':
        return flask.render_template("temp.html")
    else:
        return reply(flask.request.form['input'])

from flask import Flask, request, render_template, url_for, redirect
import flask
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from pymongo import MongoClient
import google.oauth2.credentials
import google_auth_oauthlib.flow
import json

client = MongoClient(os.environ['MONGODB_URI'])
db = client['edubuddy']
app = Flask(__name__)
app.secret_key = os.environ['secret_key']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = os.environ['local']
curr_ver = "4"
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
data_file_loc = 'app/data/course_ids'
app.static_folder = 'static'


# Force HTTPS
@app.before_request
def before_request():
    if os.environ['local'] == "0" and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    if False and ("ver" not in flask.session or flask.session["ver"] != curr_ver):
        clear_session()
        flask.session['ver'] = curr_ver
        if os.environ['local'] == '1':
            return "cleared"


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def mark_attendance():
    oauth_service = build('oauth2', 'v2',
                          credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
    email = oauth_service.userinfo().get().execute()["email"]
    if email != "aditya20016@iiitd.ac.in":
        db.store.insert_one({'purpose': "attendance", 'email': email})


def transfer_file(file_id: str, location_id: str, drive_service):
    file_metadata = {
        'parents': [location_id]
    }
    drive_service.files().copy(
        fileId=file_id,
        body=file_metadata
    ).execute()


def return_parent_drive_folder(drive_service) -> str:
    page_token = None
    while True:
        response = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and name = 'Edu-Buddy'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            return file.get("id")
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    file_metadata = {
        'name': "Edu-Buddy",
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()

    return file.get("id")


def return_storage_drive_folder(course: str, drive_service) -> str:
    session = flask.session
    session['parent_id'] = return_parent_drive_folder(drive_service)
    page_token = None
    while True:
        response = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and name = '" + course + "' and '" + session[
                'parent_id'] + "' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token).execute()
        # for file in response.get('files', []):
        #     drive_service.files().delete(fileId=file.get("id")).execute()
        #     print("Deleted", flush=True)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    file_metadata = {
        'name': course,
        'parents': [session['parent_id']],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()

    return file.get("id")


@app.route("/")
def home_view():
    clear_session()
    if 'credentials' not in flask.session:
        flask.session['scopes'] = ['https://www.googleapis.com/auth/classroom.courses.readonly',
                                   'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
                                   'https://www.googleapis.com/auth/drive',
                                   'https://www.googleapis.com/auth/userinfo.email', 'openid',
                                   'https://www.googleapis.com/auth/classroom.topics.readonly']
        flask.session['dest_after_auth'] = "/select_course"
        return flask.render_template("signin_button.html")
    else:
        return redirect("/select_course")


def generate_form(classroom_service):
    form = ''
    reply = classroom_service.courses().list().execute()['courses']
    with open(data_file_loc, 'r') as f:
        data = eval(f.read())
    for data_entry in data:
        for reply_entry in reply:
            if str(data_entry['course_id']) == str(reply_entry['id']):
                for topic_id in data_entry['topic_ids']:
                    if topic_id:
                        topic_name = \
                            classroom_service.courses().topics().get(courseId=reply_entry['id'], id=topic_id).execute()[
                                'name']
                    else:
                        topic_name = "Special Entry"
                    form += create_course_radio(name=reply_entry['name'] + ' - ' + topic_name,
                                                button_id=reply_entry['id'] + '-;-' + str(topic_id) + '-;-' +
                                                reply_entry['name'])
                    form += "\n"
                break
    return flask.Markup(form)


def handle222950113063(results, drive_service, storage_folder_id): # Handles IHCI course
    for i in results['courseWorkMaterial'][::-1]:
        try:
            if "Lecture Slides" in i['title']:
                for j in i['materials']:
                    if ".ppt" in j['driveFile']['driveFile']['title'] or ".pdf" in j['driveFile']['driveFile'][
                            'title']:
                        file_id = j['driveFile']['driveFile']['id']
                        transfer_file(file_id, storage_folder_id, drive_service=drive_service)
                        print("Transferred ", j['driveFile']['driveFile']['title'], flush=True)
        except KeyError:
            print("KeyError in ", flask.session['course'], flush=True)
            continue


@app.route("/select_course", methods=['POST', 'GET'])
def select_course():
    if request.method == 'POST':
        flask.session['course'] = request.form['course'].split('-;-')[2]

        classroom_service = build('classroom', 'v1',
                                  credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
        drive_service = build('drive', 'v3',
                              credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))

        storage_folder_id = return_storage_drive_folder(flask.session['course'], drive_service)
        page_token = None
        while True:
            results = classroom_service.courses().courseWorkMaterials().list(
                courseId=request.form['course'].split('-;-')[0],
                pageToken=page_token).execute()
            if request.form['course'].split('-;-')[0] == "222950113063": # Exception: IHCI
                handle222950113063(results, drive_service, storage_folder_id)
            else:
                for i in results['courseWorkMaterial'][::-1]:
                    try:
                        if request.form['course'].split('-;-')[1] == i['topicId']:
                            for j in i['materials']:
                                if ".ppt" in j['driveFile']['driveFile']['title'] or ".pdf" in j['driveFile']['driveFile'][
                                        'title']:
                                    file_id = j['driveFile']['driveFile']['id']
                                    transfer_file(file_id, storage_folder_id, drive_service=drive_service)
                                    print("Transferred ", j['driveFile']['driveFile']['title'], flush=True)
                    except KeyError:
                        print("KeyError in ", flask.session['course'], flush=True)
                        continue
            page_token = results.get('nextPageToken', None)
            if page_token is None:
                print("Exiting transfer", flush=True)
                break
        print("Returning redirect", flush=True)
        return redirect(url_for('final'))
    else:
        if 'credentials' in flask.session and 'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly' in \
                flask.session['credentials'][
                    'scopes'] and 'https://www.googleapis.com/auth/classroom.topics.readonly' in \
                flask.session['credentials']['scopes']:
            classroom_service = build('classroom', 'v1',
                                      credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
            return render_template("front.html", text="", form=generate_form(classroom_service))
        else:
            if 'scopes' not in flask.session:
                flask.session['scopes'] = []
            flask.session['scopes'].extend(['https://www.googleapis.com/auth/classroom.courses.readonly',
                                            'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
                                            'https://www.googleapis.com/auth/drive',
                                            'https://www.googleapis.com/auth/classroom.topics.readonly'])
            flask.session['dest_after_auth'] = "/select_course"
            return flask.redirect("/login")


@app.route("/login")
def login():
    if 'openid' not in flask.session['scopes']:
        flask.session['scopes'].append('openid')
    if 'https://www.googleapis.com/auth/userinfo.email' not in flask.session['scopes']:
        flask.session['scopes'].append('https://www.googleapis.com/auth/userinfo.email')

    flow = google_auth_oauthlib.flow.Flow.from_client_config(json.loads(os.environ['GOOGLE_SECRET']),
                                                             scopes=flask.session['scopes'])
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true",
                                                      hd="iiitd.ac.in")
    flask.session['state'] = state
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_config(json.loads(os.environ['GOOGLE_SECRET']),
                                                             scopes=flask.session['scopes'], state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    if 'poll' not in flask.session['dest_after_auth']:
        mark_attendance()

    return flask.redirect(flask.session['dest_after_auth'])


@app.route("/final")
def final():
    return render_template("final.html", id=flask.session['parent_id'])


@app.route('/clear')
def clear_session():
    flask.session.clear()
    return 'All cookies have been reset.<br><br>'


@app.route('/poll/<name>', methods=['POST', 'GET'])
def poll(name):
    if 'scopes' in flask.session.keys() and 'openid' in flask.session['scopes']:
        if request.method == 'POST':
            print(flask.session['credentials'], flush=True)
            oauth_service = build('oauth2', 'v2',
                                  credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
            email = oauth_service.userinfo().get().execute()["email"]
            db.store.insert_one({'purpose': "poll-" + name + "-" + request.form['result'], 'email': email})
            return "Your response for poll: <b>" + name + "</b> has been recorded."
        else:
            return render_template("poll.html", url="/poll/" + name)
    elif 'scopes' in flask.session.keys():
        flask.session['scopes'] += ['openid', 'https://www.googleapis.com/auth/userinfo.email']
        flask.session['dest_after_auth'] = "/poll/" + name
        return flask.render_template("signin_button.html")
    else:
        flask.session['scopes'] = ['openid', 'https://www.googleapis.com/auth/userinfo.email']
        flask.session['dest_after_auth'] = "/poll/" + name
        return flask.render_template("signin_button.html")


@app.route("/chat")
def home():
    return render_template("index.html")


def create_course_radio(name, button_id):
    return f'<p  class="box"><input type="radio" name="course" value={button_id}>{name} </p>'

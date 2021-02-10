from flask import Flask, request, render_template, url_for, redirect
import flask
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import requests
from pymongo import MongoClient
import google.oauth2.credentials
import google_auth_oauthlib.flow

client = MongoClient(os.environ['MONGODB_URI'])
db = client['edubuddy']
app = Flask(__name__)
app.secret_key = os.environ['secret_key']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = os.environ['local']


# Force HTTPS
@app.before_request
def before_request():
    if os.environ['local'] == "0" and request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


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
        db.store.insert_one({'email': email})


def transfer_file(id: str, location_id: str, drive_service):
    print(1)
    file_metadata = {
        'parents': [location_id]
    }
    print(2)
    print(3)
    drive_service.files().copy(
        fileId=id,
        body=file_metadata
    ).execute()
    print(4)


def assign_ids():
    session = flask.session
    if session['course'] == "maths":
        session['course_id'] = "249368758666"
        session['topic_id'] = "250043217503"
    elif session['course'] == "dc":
        session['course_id'] = "249364574225"
        session['topic_id'] = "249364574230"
    elif session['course'] == "ip":
        session['course_id'] = "248985762843"
        session['topic_id'] = "249714819858"
    elif session['course'] == "ihci":
        session['course_id'] = "222950113063"
        session['topic_id'] = None


def return_parent_drive_folder() -> str:
    drive_service = build('drive', 'v3',
                          credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
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


def return_storage_drive_folder(course: str) -> str:
    session = flask.session
    drive_service = build('drive', 'v3',
                          credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
    session['parent_id'] = return_parent_drive_folder()
    page_token = None
    while True:
        response = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and name = '" + session['course'] + "' and '" + session[
                'parent_id'] + "' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token).execute()
        for file in response.get('files', []):
            return file.get("id")
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
    print("Homecall", flush=True)
    if 'credentials' not in flask.session:
        print(1, flush=1)
        flask.session['scopes'] = ['https://www.googleapis.com/auth/classroom.courses.readonly', 'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/userinfo.email','openid']
        print(2, flush=1)
        flask.session['dest_after_auth'] = "/select_course"
        print(1, flush=3)
        if 'dest_after_auth' not in flask.session:
            print("ONOT HERE", flush=True)
        else:
            print("OHERE", flush=True)
        return flask.render_template("signin_button.html")
    else:
        print("Direct", flush= True)
        return redirect(url_for("select_course"))


@app.route("/select_course", methods=['POST', 'GET'])
def select_course():
    if 'credentials' not in flask.session or flask.session['scopes'] != [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/userinfo.email',
        'openid']:
        return redirect(url_for("home_view"))
    elif request.method == 'POST':
        print("oooo")
        flask.session['course'] = request.form['course']
        assign_ids()
        storage_folder_id = return_storage_drive_folder(flask.session['course'])
        classroom_service = build('classroom', 'v1',
                                  credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))
        results = classroom_service.courses().courseWorkMaterials().list(courseId=flask.session['course_id']).execute()
        drive_service = build('drive', 'v3',
                              credentials=google.oauth2.credentials.Credentials(**flask.session['credentials']))

        for i in results['courseWorkMaterial']:
            if 'topicId' in i:
                if flask.session['topic_id'] == i['topicId'] or (
                        flask.session['course'] == "ihci" and "Lecture Slides" in i['title']):
                    id = ""
                    if flask.session['course'] == "ihci" or flask.session['course'] == "maths":
                        id = i['materials'][0]['driveFile']['driveFile']['id']
                    elif flask.session['course'] == "ip":
                        for j in i['materials']:
                            if ".ppt" in j['driveFile']['driveFile']['title']:
                                id = j['driveFile']['driveFile']['id']
                                break
                    elif flask.session['course'] == "dc":
                        for j in i['materials']:
                            if "Lecture " in j['driveFile']['driveFile']['title'] and ".pdf" in \
                                    j['driveFile']['driveFile'][
                                        'title']:
                                id = j['driveFile']['driveFile']['id']
                                break
                    print("Transferring ", id)
                    transfer_file(id, storage_folder_id, drive_service=drive_service)
                    print("Transferred ", id)

        return redirect(url_for('final'))
    else:
        return render_template("select_course.html")


@app.route("/login")
def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file("app/client_secret.json",
                                                                   scopes=flask.session['scopes'])
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true",
                                                      hd="iiitd.ac.in")
    flask.session['state'] = state
    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    if 'dest_after_auth' not in flask.session:
        print("1NOT HERE", flush=True)
    else:
        print("1HERE", flush=True)
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        "app/client_secret.json", scopes=flask.session['scopes'], state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    mark_attendance()
    if 'dest_after_auth' not in flask.session:
        print("NOT HERE", flush=True)
    else:
        print("HERE", flush=True)
    return flask.redirect(flask.session['dest_after_auth'])


@app.route("/final")
def final():
    return render_template("final.html", id=flask.session['parent_id'])


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return 'Credentials successfully revoked.'
    else:
        return 'An error occurred.'


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return 'Credentials have been cleared.<br><br>'

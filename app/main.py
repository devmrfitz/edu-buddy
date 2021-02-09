from flask import Flask, request, render_template, url_for, redirect

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os
from pymongo import MongoClient
client = MongoClient(os.environ['MONGODB_URI'])
db = client.edubuddy
app = Flask(__name__)


def transfer_file(id: str, location_id: str):
    file_metadata = {
        'parents': [location_id]
    }

    drive_service.files().copy(
        fileId=id,
        body=file_metadata
    ).execute()


def assign_ids(course: str):
    global topic_id
    global course_id

    if course == "maths":
        course_id = "249368758666"
        topic_id = "250043217503"
    elif course == "dc":
        course_id = "249364574225"
        topic_id = "249364574230"
    elif course == "ip":
        course_id = "248985762843"
        topic_id = "249714819858"
    elif course == "ihci":
        course_id = "222950113063"
        topic_id = None


def return_parent_drive_folder() -> str:
    global drive_service
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
    global parent_id, drive_service
    parent_id = return_parent_drive_folder()
    page_token = None
    while True:
        response = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and name = '" + course + "' and '" + parent_id + "' in parents",
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
        'parents': [parent_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()

    return file.get("id")


@app.route("/")
def home_view():
    global credentials, offline
    offline = False
    if offline:
        credentials = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
            return redirect(url_for('select_course'))
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                with open('token.pickle', 'wb') as token:
                    pickle.dump(credentials, token)
                return redirect(url_for('select_course'))
            else:
                # auth needed
                return """<form action="/show-auth-url">  
    <input type="submit" value="Login" />
    </form>"""
    else:
        return """<form action="/show-auth-url">  
    <input type="submit" value="Login" />
    </form>"""


@app.route("/show-auth-url", methods=['POST', 'GET'])
def show_auth_url():
    global flow, offline
    if request.method == 'POST':
        global code, flow, offline
        code = request.form['code']
        flow.fetch_token(code=code)
        global credentials
        credentials = flow.credentials
        if offline:
            with open('token.pickle', 'wb') as token:
                pickle.dump(flow.credentials, token)
        return redirect(url_for('select_course'))


    else:
        CLIENT_SECRETS_FILE = "app/client_secret.json"
        SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
                  'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
                  'https://www.googleapis.com/auth/drive',
                  'https://www.googleapis.com/auth/userinfo.email',
                  'openid']

        def return_console_url(
                self,
                **kwargs
        ):
            kwargs.setdefault("prompt", "consent")
            self.redirect_uri = self._OOB_REDIRECT_URI
            auth_url, _ = self.authorization_url(**kwargs)

            return render_template("show_auth_url.html", url=auth_url)

        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        return return_console_url(flow)


def build_services():
    global drive_service, classroom_service
    classroom_service = build('classroom', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    oauth_service = build('oauth2', 'v2', credentials=credentials)
    email = oauth_service.userinfo().get().execute()["email"]
    if db.store.find({'email': email}).count() == 0:
        db.store.insert_one({'email':email})




@app.route("/select_course", methods=['POST', 'GET'])
def select_course():
    global storage_folder_id
    if request.method == 'POST':
        global course
        course = request.form['course']
        build_services()
        assign_ids(course)
        storage_folder_id = return_storage_drive_folder(course)
        results = classroom_service.courses().courseWorkMaterials().list(courseId=course_id).execute()
        for i in results['courseWorkMaterial']:
            if topic_id == i['topicId'] or (course == "ihci" and "Lecture Slides" in i['title']):
                id = ""
                if course == "ihci" or course == "maths":
                    id = i['materials'][0]['driveFile']['driveFile']['id']
                elif course == "ip":
                    for j in i['materials']:
                        if ".ppt" in j['driveFile']['driveFile']['title']:
                            id = j['driveFile']['driveFile']['id']
                            break
                elif course == "dc":
                    for j in i['materials']:
                        if "Lecture " in j['driveFile']['driveFile']['title'] and ".pdf" in j['driveFile']['driveFile'][
                            'title']:
                            id = j['driveFile']['driveFile']['id']
                            break
                transfer_file(id, storage_folder_id)


        return redirect(url_for('auth_received'))
    else:
        return render_template("select_course.html")


@app.route("/auth_received")
def auth_received():
    return """<a href='https://drive.google.com/drive/folders/""" + parent_id + """' > Link of folder</a>. """

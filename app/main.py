from flask import Flask, request, render_template, url_for, redirect

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)


@app.route("/")
def home_view():
    return """<form action="/show-auth-url">
    <input type="submit" value="Start auth" />
</form>"""


@app.route("/show-auth-url", methods=['POST', 'GET'])
def show_auth_url():
    if request.method == 'POST':
        global code
        code = request.form['code']
        return redirect(url_for('auth_received'))
    else:
        CLIENT_SECRETS_FILE = "app/client_secret.json"
        global SCOPES
        SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
                  'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly']
        global API_SERVICE_NAME
        API_SERVICE_NAME = 'classroom'
        global API_VERSION
        API_VERSION = 'v1'

        def return_console_url(
                self,
                **kwargs
        ):
            kwargs.setdefault("prompt", "consent")
            self.redirect_uri = self._OOB_REDIRECT_URI
            auth_url, _ = self.authorization_url(**kwargs)

            return render_template("show_auth_url.html", url=auth_url)

        global flow
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        return return_console_url(flow)


@app.route("/auth-received")
def auth_received():
    global code

    flow.fetch_token(code=code)

    credentials = flow.credentials
    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    def list_drive_files(service, **kwargs):
        results = service.courses().courseWorkMaterials().list(
            **kwargs
        ).execute()
        a = ""
        for i in results['courseWorkMaterial']:
            try:
                a += """
                """
                a += (i['materials'][0]['driveFile']['driveFile']['alternateLink'].split("=")[1])
            except:
                continue
        return a

    return list_drive_files(service, courseId="249368758666")

from flask import Flask, redirect, url_for, request
import types

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)

@app.route("/")
def home_iew():
    return """<form action="/show-auth-url">
    <input type="submit" value="Start auth" />
</form>"""


@app.route("/show-auth-url")
def ho():
    # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
    # the OAuth 2.0 information for this application, including its client_id and
    # client_secret.
    CLIENT_SECRETS_FILE = "app/client_secret.json"

    # This access scope grants read-only access to the authenticated user's Drive
    # account.
    global SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
              'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly']
    global API_SERVICE_NAME = 'classroom'
    global API_VERSION = 'v1'


    def return_console_url(
            self,
            authorization_prompt_message="",
            authorization_code_message="",
            **kwargs
    ):
        kwargs.setdefault("prompt", "consent")
        self.redirect_uri = self._OOB_REDIRECT_URI
        auth_url, _ = self.authorization_url(**kwargs)

        return """<h1> Authorization Page </h1>
        Please click <a href='""" + auth_url + """'>here</a>. 
<form action="/auth-received">
<label for="code">The code you get is to be entered here:</label><br>
<input type="text" id="code" value=""><br><br>
<input type="submit" value="Submit">
</form> """

    global flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    return return_console_url(flow)



@app.route("/auth-received",methods = ['POST', 'GET'])
def auth_received():

    if request.method == 'POST':
        code = request.form['code']
    else:
        code = request.args.get('code')

    flow.fetch_token(code=code)

    global credentials = flow.credentials
    global service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)



    def list_drive_files(service, **kwargs):
        results = service.courses().courseWorkMaterials().list(
            **kwargs
        ).execute()

        for i in results['courseWorkMaterial']:
            try:
                print(i['materials'][0]['driveFile']['driveFile']['alternateLink'].split("=")[1])
            except:
                continue

        # When running locally, disable OAuthlib's HTTPs verification. When
        # running in production *do not* leave this option enabled.



    list_drive_files(service, courseId="249368758666")

import os
from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
from dotenv import load_dotenv

load_dotenv()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
]
def get_auth_flow():
    return Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
    )

def fetch_user_info(credentials):
    service = googleapiclient.discovery.build(
        'oauth2', 'v2', credentials=credentials
    )
    user_info = service.userinfo().get().execute()
    return user_info

def fetch_courses(credentials):
    service = googleapiclient.discovery.build(
        'classroom', 'v1', credentials=credentials
    )
    results = service.courses().list(pageSize=100).execute()
    courses = results.get('courses', [])
    return courses

# Handle user login
import os
import json
import secrets
from flask import Flask, redirect, request, session, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from google.cloud import secretmanager
from google.oauth2.credentials import Credentials

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove in production


def get_client_secrets():
    """Fetch client secrets from Google Secret Manager"""
    project_id = os.getenv('GCP_PROJECT_ID')
    secret_id = os.getenv('SECRET_NAME', 'youtube-oauth-client-secrets')
    version_id = os.getenv('SECRET_VERSION', 'latest')
    
    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()
    
    # Build the resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    
    # Access the secret version
    response = client.access_secret_version(request={"name": name})
    
    # Parse and return the secret payload as JSON
    secret_string = response.payload.data.decode('UTF-8')
    return json.loads(secret_string)

@app.route('/')
def index():
    if 'credentials' not in session:
        return '<h1>YouTube OAuth</h1><a href="/login">Login with Google</a>'
    # return '<h1>Logged in!</h1><a href="/channel">View Channel</a> | <a href="/logout">Logout</a>'
    
    return '''
    <h1>Logged in!</h1>
    <ul>
        <li><a href="/channel">View Channel Info</a></li>
        <li><a href="/playlists">View Playlists</a></li>
        <li><a href="/logout">Logout</a></li>
    </ul>
    '''

@app.route('/login')
def login():
    client_config = get_client_secrets()
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )

    auth_url, state = flow.authorization_url(access_type='offline')
    session['state'] = state
    return redirect(auth_url)


@app.route('/callback')
def callback():
    client_config = get_client_secrets()
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )
    
    flow.fetch_token(authorization_response=request.url)
    
    session['credentials'] = {
        'token': flow.credentials.token,
        'refresh_token': flow.credentials.refresh_token,
        'token_uri': flow.credentials.token_uri,
        'client_id': flow.credentials.client_id,
        'client_secret': flow.credentials.client_secret,
        'scopes': flow.credentials.scopes
    }

    return redirect('/')

@app.route('/channel')
def channel():
    if 'credentials' not in session:
        return redirect('/login')

    creds = Credentials(**session['credentials'])
    youtube = build('youtube', 'v3', credentials=creds)

    response = youtube.channels().list(part='snippet,statistics', mine=True).execute()
    channel = response['items'][0]

    return f'''
    <h1>{channel['snippet']['title']}</h1>
    <p>Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}</p>
    <p>Views: {channel['statistics']['viewCount']}</p>
    <p><a href="/">Home</a></p>
    '''

@app.route('/playlists')
def playlists():
    if 'credentials' not in session:
        return redirect('/login')
    
    creds = Credentials(**session['credentials'])
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Get user's playlists
    response = youtube.playlists().list(
        part='snippet,contentDetails',
        mine=True,
        maxResults=50
    ).execute()
    
    html = '<h1>Your Playlists</h1>'
    
    if not response.get('items'):
        html += '<p>No playlists found.</p>'
    else:
        html += '<ul>'
        for item in response['items']:
            title = item['snippet']['title']
            playlist_id = item['id']
            item_count = item['contentDetails']['itemCount']
            html += f'<li><strong>{title}</strong> - {item_count} videos (ID: {playlist_id})</li>'
        html += '</ul>'
    
    html += '<p><a href="/channel">Back to Channel</a> | <a href="/">Home</a></p>'
    return html

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__': 
    print('Starting Flask app...')
    print('Visit http://localhost:5000 in your browser')
    print('Available routes:')
    
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    
    app.run(debug=True, host='localhost', port=5000)

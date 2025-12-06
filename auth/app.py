
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
from datetime import datetime

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
    return '<h1>Logged in!</h1><a href="/channel">View Channel</a> | <a href="/logout">Logout</a>'
    

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

    
    # Get user data history after login
    
    watch_history = get_watch_history()
    print(f"\n{json.dumps(watch_history, indent=2)=}\n")

    playlists = get_playlists()
    print(f"\n{playlists=}\n")

    channel_info = get_channel_info()
    print(f"\n{channel_info=}\n")

    return redirect('/')

# @app.route('/channel')
def get_channel_info():
    if 'credentials' not in session:
        return redirect('/login')

    creds = Credentials(**session['credentials'])
    youtube = build('youtube', 'v3', credentials=creds)

    response = youtube.channels().list(part='snippet,statistics', mine=True).execute()
    channel = response['items'][0]

    channel_data = {
        'channel_id': channel['id'],
        'title': channel['snippet']['title'],
        'description': channel['snippet'].get('description', ''),
        'custom_url': channel['snippet'].get('customUrl', ''),
        'published_at': channel['snippet']['publishedAt'],
        'thumbnail': channel['snippet']['thumbnails'].get('high', {}).get('url', ''),
        'statistics': {
            'subscriber_count': channel['statistics'].get('subscriberCount', 'Hidden'),
            'video_count': channel['statistics'].get('videoCount', '0'),
            'view_count': channel['statistics'].get('viewCount', '0')
        }
    }
        
    return {'channel_info': channel_data} 
    """
    return f'''
    <h1>{channel['snippet']['title']}</h1>
    <p>Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}</p>
    <p>Views: {channel['statistics']['viewCount']}</p>
    <p><a href="/">Home</a></p>
    '''
    """

# @app.route('/playlists')
def get_playlists():
    if 'credentials' not in session:
        return redirect('/login')
    
    creds = Credentials(**session['credentials'])
    youtube = build('youtube', 'v3', credentials=creds)
    playlists = []   
 
    # Get user's playlists
    response = youtube.playlists().list(
        part='snippet,contentDetails',
        mine=True,
        maxResults=50
    ).execute()
    
    # html = '<h1>Your Playlists</h1>'
    """
    if not response.get('items'):
        print("No playlists found")
          
        html += '<p>No playlists found.</p>'
    else:
        return
        html += '<ul>'
        for item in response['items']:
            title = item['snippet']['title']
            playlist_id = item['id']
            item_count = item['contentDetails']['itemCount']
            html += f'<li><strong>{title}</strong> - {item_count} videos (ID: {playlist_id})</li>'
        html += '</ul>'
    
    html += '<p><a href="/channel">Back to Channel</a> | <a href="/">Home</a></p>'
    return html
    """

    for item in response.get('items', []):
        playlist_data = {
            'playlist_id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet'].get('description', ''),
            'item_count': item['contentDetails']['itemCount'],
            'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url', '')
        }

        playlists.append(playlist_data)
    
    return {'playlists': playlists}

# @app.route('/watch-history')
"""
def get_watch_history():
    if 'credentials' not in session:
        return redirect('/login')
    
    creds = Credentials(**session['credentials'])
    youtube = build('youtube', 'v3', credentials=creds)
    
    try:
        watch_history = []
        
        # Get user activities (watch history)
        activities_response = youtube.activities().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50
        ).execute()
        
        for activity in activities_response.get('items', []):
            snippet = activity['snippet']
            content_details = activity.get('contentDetails', {})
            
            video_id = None
            
            # Extract video ID from different activity types
            if 'upload' in content_details:
                video_id = content_details['upload'].get('videoId')
            elif 'playlistItem' in content_details:
                video_id = content_details['playlistItem'].get('resourceId', {}).get('videoId')
            elif 'like' in content_details:
                video_id = content_details['like'].get('resourceId', {}).get('videoId')
            elif 'recommendation' in content_details:
                video_id = content_details['recommendation'].get('resourceId', {}).get('videoId')
            
            if video_id:
                try:
                    # Get detailed video information
                    video_response = youtube.videos().list(
                        part='snippet,contentDetails,statistics',
                        id=video_id
                    ).execute()
                    
                    if video_response.get('items'):
                        video = video_response['items'][0]
                        video_snippet = video['snippet']
                        
                        # Parse duration to seconds (format: PT#M#S)
                        duration = video['contentDetails'].get('duration', 'PT0S')
                        watch_time_seconds = parse_duration(duration)
                        
                        video_data = {
                            'video_id': video_id,
                            'title': video_snippet['title'],
                            'channel': video_snippet['channelTitle'],
                            'watched_at': snippet['publishedAt'],
                            'watch_time_seconds': watch_time_seconds,
                            'thumbnail': video_snippet['thumbnails'].get('maxresdefault', video_snippet['thumbnails'].get('high', {})).get('url', ''),
                            'tags': video_snippet.get('tags', [])
                        }
                        
                        watch_history.append(video_data)
                except Exception as e:
                    print(f"Error fetching video {video_id}: {str(e)}")
                    continue
        
        result = {
            'user_profile': {
                'interests': [],
                'preferred_channels': []
            },
            'watch_history': watch_history
        }
        
        return result
        
    except Exception as e:
        return {'error': str(e)}, 500
"""
def get_watch_history(youtube):
    """Get watch history from YouTube API"""
    try:
        watch_history = []
        
        # Try to get the "Watch History" playlist
        # First, get channel info to find special playlists
        channels_response = youtube.channels().list(
            part='contentDetails',
            mine=True
        ).execute()
        
        if channels_response.get('items'):
            # Check for watch history playlist
            content_details = channels_response['items'][0].get('contentDetails', {})
            related_playlists = content_details.get('relatedPlaylists', {})
            
            # Try to get watch history from the history playlist if it exists
            # Note: This may not be accessible via API
            
            # Get liked videos instead (more reliable)
            liked_playlist_id = related_playlists.get('likes')
            
            if liked_playlist_id:
                playlist_response = youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=liked_playlist_id,
                    maxResults=50
                ).execute()
                
                for item in playlist_response.get('items', []):
                    video_id = item['contentDetails']['videoId']
                    
                    try:
                        # Get detailed video information
                        video_response = youtube.videos().list(
                            part='snippet,contentDetails,statistics',
                            id=video_id
                        ).execute()
                        
                        if video_response.get('items'):
                            video = video_response['items'][0]
                            video_snippet = video['snippet']
                            
                            # Parse duration to seconds
                            duration = video['contentDetails'].get('duration', 'PT0S')
                            watch_time_seconds = parse_duration(duration)
                            
                            video_data = {
                                'video_id': video_id,
                                'title': video_snippet['title'],
                                'channel': video_snippet['channelTitle'],
                                'watched_at': item['snippet']['publishedAt'],
                                'watch_time_seconds': watch_time_seconds,
                                'thumbnail': video_snippet['thumbnails'].get('maxresdefault', video_snippet['thumbnails'].get('high', {})).get('url', ''),
                                'tags': video_snippet.get('tags', [])
                            }
                            
                            watch_history.append(video_data)
                    except Exception as e:
                        print(f"Error fetching video {video_id}: {str(e)}")
                        continue
        
        # If no liked videos, fall back to activities
        if not watch_history:
            activities_response = youtube.activities().list(
                part='snippet,contentDetails',
                mine=True,
                maxResults=50
            ).execute()
            
            for activity in activities_response.get('items', []):
                snippet = activity['snippet']
                content_details = activity.get('contentDetails', {})
                
                video_id = None
                
                # Extract video ID from different activity types
                if 'upload' in content_details:
                    video_id = content_details['upload'].get('videoId')
                elif 'playlistItem' in content_details:
                    video_id = content_details['playlistItem'].get('resourceId', {}).get('videoId')
                elif 'like' in content_details:
                    video_id = content_details['like'].get('resourceId', {}).get('videoId')
                elif 'recommendation' in content_details:
                    video_id = content_details['recommendation'].get('resourceId', {}).get('videoId')
                
                if video_id:
                    try:
                        # Get detailed video information
                        video_response = youtube.videos().list(
                            part='snippet,contentDetails,statistics',
                            id=video_id
                        ).execute()
                        
                        if video_response.get('items'):
                            video = video_response['items'][0]
                            video_snippet = video['snippet']
                            
                            duration = video['contentDetails'].get('duration', 'PT0S')
                            watch_time_seconds = parse_duration(duration)
                            
                            video_data = {
                                'video_id': video_id,
                                'title': video_snippet['title'],
                                'channel': video_snippet['channelTitle'],
                                'watched_at': snippet['publishedAt'],
                                'watch_time_seconds': watch_time_seconds,
                                'thumbnail': video_snippet['thumbnails'].get('maxresdefault', video_snippet['thumbnails'].get('high', {})).get('url', ''),
                                'tags': video_snippet.get('tags', [])
                            }
                            
                            watch_history.append(video_data)
                    except Exception as e:
                        print(f"Error fetching video {video_id}: {str(e)}")
                        continue
        
        result = {
            'user_profile': {
                'interests': [],
                'preferred_channels': []
            },
            'watch_history': watch_history
        }
        
        return result
        
    except Exception as e:
        return {'error': str(e)}

def parse_duration(duration_str):
    """Convert ISO 8601 duration (PT#H#M#S) to seconds"""
    import re
    
    # Remove PT prefix
    duration_str = duration_str.replace('PT', '')
    
    hours = 0
    minutes = 0
    seconds = 0
    
    # Extract hours
    hours_match = re.search(r'(\d+)H', duration_str)
    if hours_match:
        hours = int(hours_match.group(1))
    
    # Extract minutes
    minutes_match = re.search(r'(\d+)M', duration_str)
    if minutes_match:
        minutes = int(minutes_match.group(1))
    
    # Extract seconds
    seconds_match = re.search(r'(\d+)S', duration_str)
    if seconds_match:
        seconds = int(seconds_match.group(1))
    
    return hours * 3600 + minutes * 60 + seconds

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':  
    app.run(debug=True, host='localhost', port=5001)

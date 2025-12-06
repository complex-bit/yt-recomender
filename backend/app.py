from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from recommendation_engine import RecommendationEngine

app = Flask(__name__)
CORS(app)

# Global variable to store watch history data
watch_history_data = None
recommendation_engine = None

def load_watch_history():
    """Load watch history from JSON file on startup"""
    global watch_history_data, recommendation_engine
    try:
        # Try Docker path first, then local development path
        docker_path = '/app/youtube_watch_history.json'
        local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'youtube_watch_history.json')

        if os.path.exists(docker_path):
            json_path = docker_path
            db_path = '/app/youtube_videos.db'
        else:
            json_path = local_path
            db_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')

        with open(json_path, 'r') as file:
            watch_history_data = json.load(file)
        print(f"Loaded {len(watch_history_data['watch_history'])} videos from watch history")

        # Initialize recommendation engine
        recommendation_engine = RecommendationEngine(db_path, json_path)
        recommendation_engine.load_user_preferences()
        print("Recommendation engine initialized")

    except Exception as e:
        print(f"Error loading watch history: {e}")
        watch_history_data = {"watch_history": []}

def analyze_top_channels():
    """Analyze watch history to get top 5 channels"""
    if not watch_history_data:
        return []

    channel_counts = Counter()
    channel_info = {}

    for video in watch_history_data['watch_history']:
        # Handle both old format (channelId) and new format (channel)
        channel_id = video.get('channelId') or video.get('channel')
        channel_title = video.get('channelTitle') or video.get('channel')

        if channel_id:
            channel_counts[channel_id] += 1

            # Store channel info (take the latest one)
            if channel_id not in channel_info:
                # Use the first category if it's a list, otherwise use the string
                category = video.get('categories', ['Unknown'])
                if isinstance(category, list):
                    category = category[0] if category else 'Unknown'

                channel_info[channel_id] = {
                    'channelTitle': channel_title,
                    'category': category,
                    'channelAvatar': video.get('channelAvatar', '')
                }

    # Get top 5 channels
    top_channels = []
    for channel_id, count in channel_counts.most_common(5):
        channel_data = {
            'channelId': channel_id,
            'channelTitle': channel_info[channel_id]['channelTitle'],
            'watchCount': count,
            'category': channel_info[channel_id]['category']
        }

        # Add avatar if available
        if channel_info[channel_id]['channelAvatar']:
            channel_data['channelAvatar'] = channel_info[channel_id]['channelAvatar']

        top_channels.append(channel_data)

    return top_channels

def analyze_genre_percentages():
    """Analyze watch history to get genre distribution"""
    if not watch_history_data:
        return {}

    category_counts = Counter()
    tag_counts = Counter()
    total_videos = len(watch_history_data['watch_history'])

    for video in watch_history_data['watch_history']:
        # Handle categories as list or string
        categories = video.get('categories', [])
        if isinstance(categories, str):
            categories = [categories]
        elif not isinstance(categories, list):
            categories = []

        # Count each category
        for category in categories:
            if category:
                category_counts[category] += 1

        # Also count tags for more granular analysis
        for tag in video.get('tags', []):
            tag_counts[tag] += 1

    # Convert to percentages and map to genre tree structure
    genre_percentages = {}
    for category, count in category_counts.items():
        percentage = round((count / total_videos) * 100)

        # Map YouTube categories to our genre tree
        if 'Documentary' in category or 'documentary' in category.lower():
            genre_percentages['documentary'] = percentage
        elif 'Science' in category or 'Technology' in category:
            genre_percentages['tech'] = percentage
        elif 'Education' in category:
            genre_percentages['education'] = percentage
        elif 'Entertainment' in category:
            genre_percentages['entertainment'] = percentage

    return genre_percentages

def generate_dynamic_genre_tree():
    """Generate hierarchical genre tree: Primary > Secondary > Sub > Sub-Sub"""
    try:
        import sqlite3

        # Query database for ALL genre classifications to show full genre exploration options
        conn = sqlite3.connect('youtube_videos.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT primary_genre, secondary_genre, sub_genre, sub_sub_genre, COUNT(*) as count
            FROM video_genres
            WHERE primary_genre IS NOT NULL
            GROUP BY primary_genre, secondary_genre, sub_genre, sub_sub_genre
            ORDER BY count DESC
        ''')

        genre_data = cursor.fetchall()
        conn.close()

        if not genre_data:
            return []

        # Build hierarchical tree
        primary_genres = {}

        for primary, secondary, sub, sub_sub, count in genre_data:
            if not primary:
                continue

            # Initialize primary genre
            if primary not in primary_genres:
                primary_genres[primary] = {
                    'name': primary,
                    'count': 0,
                    'children': {}
                }

            primary_genres[primary]['count'] += count

            # Add secondary genre
            if secondary:
                if secondary not in primary_genres[primary]['children']:
                    primary_genres[primary]['children'][secondary] = {
                        'name': secondary,
                        'count': 0,
                        'children': {}
                    }

                primary_genres[primary]['children'][secondary]['count'] += count

                # Add sub genre
                if sub:
                    if sub not in primary_genres[primary]['children'][secondary]['children']:
                        primary_genres[primary]['children'][secondary]['children'][sub] = {
                            'name': sub,
                            'count': 0,
                            'children': {}
                        }

                    primary_genres[primary]['children'][secondary]['children'][sub]['count'] += count

                    # Add sub-sub genre
                    if sub_sub:
                        if sub_sub not in primary_genres[primary]['children'][secondary]['children'][sub]['children']:
                            primary_genres[primary]['children'][secondary]['children'][sub]['children'][sub_sub] = {
                                'name': sub_sub,
                                'count': 0
                            }

                        primary_genres[primary]['children'][secondary]['children'][sub]['children'][sub_sub]['count'] += count

        # Convert to genre wheel format
        genre_tree = []
        total_videos = sum(primary_data['count'] for primary_data in primary_genres.values())

        for primary_name, primary_data in sorted(primary_genres.items(), key=lambda x: x[1]['count'], reverse=True):
            # Build secondary level
            secondary_children = []
            for sec_name, sec_data in sorted(primary_data['children'].items(), key=lambda x: x[1]['count'], reverse=True)[:8]:
                # Build sub level
                sub_children = []
                for sub_name, sub_data in sorted(sec_data['children'].items(), key=lambda x: x[1]['count'], reverse=True)[:6]:
                    # Build sub-sub level
                    sub_sub_children = []
                    if 'children' in sub_data:
                        for sub_sub_name, sub_sub_data in sorted(sub_data['children'].items(), key=lambda x: x[1]['count'], reverse=True)[:4]:
                            sub_sub_children.append({
                                'id': f"{primary_name}_{sec_name}_{sub_name}_{sub_sub_name}".lower().replace(' ', '_'),
                                'name': sub_sub_name,
                                'count': sub_sub_data['count'],
                                'level': 4,
                                'path': [primary_name, sec_name, sub_name, sub_sub_name]
                            })

                    sub_children.append({
                        'id': f"{primary_name}_{sec_name}_{sub_name}".lower().replace(' ', '_'),
                        'name': sub_name,
                        'count': sub_data['count'],
                        'level': 3,
                        'path': [primary_name, sec_name, sub_name],
                        'children': sub_sub_children if sub_sub_children else None
                    })

                secondary_children.append({
                    'id': f"{primary_name}_{sec_name}".lower().replace(' ', '_'),
                    'name': sec_name,
                    'count': sec_data['count'],
                    'level': 2,
                    'path': [primary_name, sec_name],
                    'children': sub_children if sub_children else None
                })

            genre_tree.append({
                'id': primary_name.lower().replace(' ', '_'),
                'name': primary_name,
                'percentage': round((primary_data['count'] / total_videos) * 100),
                'count': primary_data['count'],
                'level': 1,
                'path': [primary_name],
                'children': secondary_children if secondary_children else None
            })

        return genre_tree[:6]  # Top 6 primary genres

    except Exception as e:
        print(f"Error generating hierarchical genre tree: {e}")
        return []

def create_fallback_genre_tree():
    """Create a fallback genre tree from channels and basic categorization"""
    if not watch_history_data:
        return []

    # Create simple tree based on top channels
    channel_counts = Counter()
    for video in watch_history_data['watch_history']:
        channel = video.get('channel') or video.get('channelTitle')
        if channel:
            channel_counts[channel] += 1

    total_videos = len(watch_history_data['watch_history'])

    # Group channels by type
    educational_channels = ['Veritasium', '3Blue1Brown', 'Kurzgesagt', 'SmarterEveryDay']
    history_channels = ['OverSimplified', 'Crash Course', 'Extra History']
    science_channels = ['NileRed', 'Steve1989MREInfo', 'Technology Connections']

    genre_tree = []

    # Education category
    edu_count = sum(count for channel, count in channel_counts.items()
                   if channel in educational_channels)
    if edu_count > 0:
        children = [{'id': f'edu_{channel.lower()}', 'name': channel, 'count': count}
                   for channel, count in channel_counts.items()
                   if channel in educational_channels]

        genre_tree.append({
            'id': 'education',
            'name': 'Educational Content',
            'percentage': round((edu_count / total_videos) * 100),
            'children': children
        })

    # History category
    hist_count = sum(count for channel, count in channel_counts.items()
                    if channel in history_channels)
    if hist_count > 0:
        children = [{'id': f'hist_{channel.lower()}', 'name': channel, 'count': count}
                   for channel, count in channel_counts.items()
                   if channel in history_channels]

        genre_tree.append({
            'id': 'history',
            'name': 'History & Stories',
            'percentage': round((hist_count / total_videos) * 100),
            'children': children
        })

    # Science category
    sci_count = sum(count for channel, count in channel_counts.items()
                   if channel in science_channels)
    if sci_count > 0:
        children = [{'id': f'sci_{channel.lower()}', 'name': channel, 'count': count}
                   for channel, count in channel_counts.items()
                   if channel in science_channels]

        genre_tree.append({
            'id': 'science',
            'name': 'Science & Tech',
            'percentage': round((sci_count / total_videos) * 100),
            'children': children
        })

    return genre_tree

@app.route('/api/profile', methods=['GET'])
def get_user_profile():
    """Get user taste profile (top channels + genre percentages + dynamic genre tree)"""
    top_channels = analyze_top_channels()
    genre_percentages = analyze_genre_percentages()
    genre_tree = generate_dynamic_genre_tree()

    return jsonify({
        'topChannels': top_channels,
        'genrePercentages': genre_percentages,
        'genreTree': genre_tree,
        'totalVideos': len(watch_history_data['watch_history']) if watch_history_data else 0
    })

@app.route('/api/search', methods=['POST'])
def search_videos():
    """Search videos based on query and filters"""
    if not watch_history_data:
        return jsonify({'videos': [], 'total': 0})

    data = request.json
    search_query = data.get('query', '').lower()
    genre_path = data.get('genrePath', [])
    refinements = data.get('refinements', {})

    # Start with all videos
    videos = watch_history_data['watch_history'].copy()

    # Filter by search query (title, tags, channel, description)
    if search_query:
        filtered_videos = []
        for video in videos:
            title_match = search_query in video['title'].lower()
            description_match = search_query in video.get('description', '').lower()
            channel_match = search_query in video['channelTitle'].lower()

            # Handle tags as list
            tags = video.get('tags', [])
            if isinstance(tags, list):
                tag_match = any(search_query in tag.lower() for tag in tags if tag)
            else:
                tag_match = False

            if title_match or tag_match or channel_match or description_match:
                filtered_videos.append(video)
        videos = filtered_videos

    # Filter by genre path (basic mapping)
    if genre_path:
        # Handle both string and dict formats for genre_path
        if isinstance(genre_path, list) and len(genre_path) > 0:
            last_genre_item = genre_path[-1]
            if isinstance(last_genre_item, dict):
                last_genre = last_genre_item.get('name', '').lower()
            else:
                last_genre = str(last_genre_item).lower()
        else:
            last_genre = ''

        if last_genre:
            filtered_videos = []
            for video in videos:
                # Handle categories as list
                categories = video.get('categories', [])
                if isinstance(categories, str):
                    categories = [categories]
                elif not isinstance(categories, list):
                    categories = []

                category_match = any(last_genre in category.lower() for category in categories if category)

                # Handle tags as list
                tags = video.get('tags', [])
                if isinstance(tags, list):
                    tag_match = any(last_genre in tag.lower() for tag in tags if tag)
                else:
                    tag_match = False

                if category_match or tag_match:
                    filtered_videos.append(video)
            videos = filtered_videos

    # Apply refinement filters
    if refinements:
        # Length filter (convert slider value to duration range)
        length_val = refinements.get('length', 50)
        if length_val < 30:  # Short videos
            videos = [v for v in videos if v['duration'] < 900]  # < 15 min
        elif length_val > 70:  # Long videos
            videos = [v for v in videos if v['duration'] > 1800]  # > 30 min

        # Popularity filter (mock implementation)
        popularity_val = refinements.get('popularity', 50)
        if popularity_val < 30:  # Hidden gems - no specific filter for now
            pass
        elif popularity_val > 70:  # Popular hits - no specific filter for now
            pass

    return jsonify({
        'videos': videos,
        'total': len(videos),
        'query': search_query,
        'genrePath': genre_path
    })

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get personalized video recommendations"""
    if not recommendation_engine:
        return jsonify({'error': 'Recommendation engine not initialized'}), 500

    # Get query parameters
    limit = request.args.get('limit', 20, type=int)
    educational_level = request.args.get('educational_level')
    min_duration = request.args.get('min_duration', type=int)
    max_duration = request.args.get('max_duration', type=int)
    popularity = request.args.get('popularity', type=int)  # 0-100 slider
    recency = request.args.get('recency', type=int)  # 0-100 slider
    uniqueness = request.args.get('uniqueness', type=int)  # 0-100 slider
    channels = request.args.getlist('channels')
    genre_path = request.args.getlist('genre_path')  # For genre selection

    # Build filters
    filters = {}
    if educational_level:
        filters['educational_level'] = educational_level
    if min_duration:
        filters['min_duration'] = min_duration
    if max_duration:
        filters['max_duration'] = max_duration
    if channels:
        filters['channels'] = channels
    if genre_path:
        filters['genre_path'] = genre_path
    if popularity is not None:
        filters['popularity'] = popularity
    if recency is not None:
        filters['recency'] = recency
    if uniqueness is not None:
        filters['uniqueness'] = uniqueness

    try:
        recommendations = recommendation_engine.get_recommendations(limit, filters)
        return jsonify({
            'recommendations': recommendations,
            'total': len(recommendations),
            'filters_applied': filters
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_user_analytics():
    """Get user viewing analytics"""
    if not recommendation_engine:
        return jsonify({'error': 'Recommendation engine not initialized'}), 500

    try:
        analytics = recommendation_engine.get_user_analytics()
        return jsonify(analytics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos/<video_id>/feedback', methods=['POST'])
def video_feedback(video_id):
    """Store video feedback (thumbs up/down)"""
    data = request.json
    feedback = data.get('feedback')  # 'up' or 'down'

    # For MVP, just acknowledge the feedback
    # In production, you'd store this in a database
    print(f"Video {video_id} received feedback: {feedback}")

    return jsonify({'status': 'success', 'videoId': video_id, 'feedback': feedback})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'WhyExplore API is running!',
        'endpoints': ['/api/profile', '/api/search', '/health'],
        'videos_loaded': len(watch_history_data['watch_history']) if watch_history_data else 0
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'videos_loaded': len(watch_history_data['watch_history']) if watch_history_data else 0
    })

if __name__ == '__main__':
    # Load watch history on startup
    load_watch_history()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
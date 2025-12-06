from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from collections import Counter, defaultdict
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global variable to store watch history data
watch_history_data = None

def load_watch_history():
    """Load watch history from JSON file on startup"""
    global watch_history_data
    try:
        # Try Docker path first, then local development path
        docker_path = '/app/youtube_watch_history.json'
        local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'youtube_watch_history.json')

        if os.path.exists(docker_path):
            json_path = docker_path
        else:
            json_path = local_path

        with open(json_path, 'r') as file:
            watch_history_data = json.load(file)
        print(f"Loaded {len(watch_history_data['watch_history'])} videos from watch history")
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
        channel_id = video['channelId']
        channel_counts[channel_id] += 1

        # Store channel info (take the latest one)
        if channel_id not in channel_info:
            # Use the first category if it's a list, otherwise use the string
            category = video.get('categories', ['Unknown'])
            if isinstance(category, list):
                category = category[0] if category else 'Unknown'

            channel_info[channel_id] = {
                'channelTitle': video['channelTitle'],
                'category': category,
                'channelAvatar': video.get('channelAvatar')
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
    """Generate genre tree based on user's actual watch history"""
    if not watch_history_data:
        return []

    category_counts = Counter()
    tag_counts = defaultdict(Counter)

    for video in watch_history_data['watch_history']:
        # Handle categories as list or string
        categories = video.get('categories', [])
        if isinstance(categories, str):
            categories = [categories]
        elif not isinstance(categories, list):
            categories = []

        for category in categories:
            if category:
                category_counts[category] += 1

                # Group tags by category
                for tag in video.get('tags', []):
                    if tag:
                        tag_counts[category][tag] += 1

    total_videos = len(watch_history_data['watch_history'])
    genre_tree = []

    # Create nodes for each major category
    for category, count in category_counts.most_common():
        percentage = round((count / total_videos) * 100)

        # Get top tags for this category as subcategories
        top_tags = tag_counts[category].most_common(8)  # Top 8 tags
        children = []

        for tag, tag_count in top_tags:
            if tag_count > 1:  # Only include tags that appear multiple times
                children.append({
                    'id': f"{category.lower().replace(' & ', '_').replace(' ', '_')}_{tag.replace(' ', '_')}",
                    'name': tag.title(),
                    'count': tag_count
                })

        # Map category to friendly names and IDs
        category_id = category.lower().replace(' & ', '_').replace(' ', '_')
        category_name = category

        if 'science' in category.lower() and 'technology' in category.lower():
            category_id = 'tech'
            category_name = 'Technology & Engineering'
        elif 'documentary' in category.lower():
            category_id = 'documentary'
            category_name = 'Documentaries'

        genre_tree.append({
            'id': category_id,
            'name': category_name,
            'percentage': percentage,
            'children': children if len(children) > 0 else None
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
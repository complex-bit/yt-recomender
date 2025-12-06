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
            db_path = '/app/data/youtube_videos.db'
        else:
            json_path = local_path
            db_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')

        with open(json_path, 'r') as file:
            watch_history_data = json.load(file)
        print(f"Loaded {len(watch_history_data['watch_history'])} videos from watch history")

        # Initialize recommendation engine
        try:
            recommendation_engine = RecommendationEngine(db_path, json_path)
            recommendation_engine.load_user_preferences()
            print("Recommendation engine initialized")
        except Exception as e:
            print(f"Error initializing recommendation engine: {e}")
            recommendation_engine = None

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
        channel_title = video.get('channel') or video.get('channelTitle', '')

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

def get_saved_genre_tree():
    """Get saved genre tree from database"""
    try:
        import sqlite3
        import json

        # Use the same path logic as load_watch_history
        docker_path = '/app/data/youtube_videos.db'
        local_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')
        db_path = docker_path if os.path.exists(docker_path) else local_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT tree_data FROM user_genre_tree ORDER BY updated_at DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return None
    except Exception as e:
        print(f"Error getting saved genre tree: {e}")
        return None

def save_genre_tree(tree_data):
    """Save genre tree to database"""
    try:
        import sqlite3
        import json

        # Use the same path logic as load_watch_history
        docker_path = '/app/data/youtube_videos.db'
        local_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')
        db_path = docker_path if os.path.exists(docker_path) else local_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Clear existing trees (keep only one)
        cursor.execute('DELETE FROM user_genre_tree')

        # Save new tree
        cursor.execute(
            'INSERT INTO user_genre_tree (tree_data) VALUES (?)',
            (json.dumps(tree_data),)
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving genre tree: {e}")
        return False

def generate_personalized_genre_tree(force_new=False):
    """Generate personalized genre tree using actual database genres"""
    if not watch_history_data:
        return []

    # Check for saved tree first (unless force_new is True)
    if not force_new:
        saved_tree = get_saved_genre_tree()
        if saved_tree:
            return saved_tree

    try:
        import openai
        import os
        import sqlite3

        # Get available database genres first
        # Use the same path logic as load_watch_history
        docker_path = '/app/data/youtube_videos.db'
        local_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')
        db_path = docker_path if os.path.exists(docker_path) else local_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT primary_genre, secondary_genre, sub_genre, COUNT(*) as count
            FROM video_genres
            WHERE primary_genre IS NOT NULL
            GROUP BY primary_genre, secondary_genre, sub_genre
            ORDER BY count DESC
        ''')

        available_genres = cursor.fetchall()
        conn.close()

        # Create a structure of available genres
        genre_structure = {}
        for primary, secondary, sub, count in available_genres:
            if primary not in genre_structure:
                genre_structure[primary] = {}
            if secondary and secondary not in genre_structure[primary]:
                genre_structure[primary][secondary] = []
            if sub and secondary:
                genre_structure[primary][secondary].append(sub)

        # Extract all tags from user's watch history
        all_tags = []
        for video in watch_history_data['watch_history']:
            tags = video.get('tags', [])
            all_tags.extend(tags)

        unique_tags = list(set(all_tags))

        if not unique_tags:
            return generate_fallback_genre_tree_from_watched()

        # Use OpenAI to map user tags to actual database genres
        openai.api_key = os.getenv('OPENAI_API_KEY')

        tags_string = ', '.join(unique_tags)
        available_genres_text = str(genre_structure)

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a YouTube content categorization expert. Map user interests to existing database genres."
            }, {
                "role": "user",
                "content": f"""Based on these tags from a user's watch history, create a genre tree using ONLY the available genres from the database.

User tags: {tags_string}

Available database genres: {available_genres_text}

Create a JSON structure with 3-4 primary categories that match the user's interests. Use ONLY the exact genre names from the database structure provided above.

Return format:
[
  {{
    "primary": "Education",
    "secondary": ["History", "Science"],
    "relevance": 0.9
  }}
]

Map the user's tags to the most relevant existing database genres. Be selective - only include genres that truly match the user's interests."""
            }],
            temperature=0.3
        )

        import json
        mapping_text = response.choices[0].message.content

        # Extract JSON from response
        start_idx = mapping_text.find('[')
        end_idx = mapping_text.rfind(']') + 1
        if start_idx >= 0 and end_idx > start_idx:
            mapping_json = mapping_text[start_idx:end_idx]
            genre_mapping = json.loads(mapping_json)

            # Build tree using actual database genres
            formatted_tree = []

            for i, mapping in enumerate(genre_mapping[:4]):  # Limit to 4 categories
                primary = mapping.get('primary')
                secondary_list = mapping.get('secondary', [])
                relevance = mapping.get('relevance', 0.5)

                if primary in genre_structure:
                    category_data = {
                        'id': primary.lower().replace(' ', '_').replace('&', 'and'),
                        'name': primary,
                        'percentage': int(relevance * 100),
                        'level': 1,
                        'path': [primary],
                        'children': []
                    }

                    for secondary in secondary_list:
                        if secondary in genre_structure[primary]:
                            sub_data = {
                                'id': f"{category_data['id']}_{secondary.lower().replace(' ', '_')}",
                                'name': secondary,
                                'level': 2,
                                'path': [primary, secondary],
                                'children': []
                            }

                            # Add sub-genres
                            for sub in genre_structure[primary][secondary][:3]:  # Limit to 3
                                topic_data = {
                                    'id': f"{sub_data['id']}_{sub.lower().replace(' ', '_')}",
                                    'name': sub,
                                    'level': 3,
                                    'path': [primary, secondary, sub]
                                }
                                sub_data['children'].append(topic_data)

                            category_data['children'].append(sub_data)

                    formatted_tree.append(category_data)

            # Save the generated tree
            save_genre_tree(formatted_tree)
            return formatted_tree

    except Exception as e:
        print(f"Error generating personalized genre tree with ChatGPT: {e}")
        return generate_fallback_genre_tree_from_watched()

def generate_fallback_genre_tree_from_watched():
    """Generate genre tree only from videos the user has actually watched"""
    if not watch_history_data:
        return []

    try:
        import sqlite3

        # Get genre classifications only for watched videos
        watched_video_ids = [v.get('video_id') for v in watch_history_data['watch_history'] if v.get('video_id')]

        if not watched_video_ids:
            return []

        # Use the same path logic as load_watch_history
        docker_path = '/app/data/youtube_videos.db'
        local_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')
        db_path = docker_path if os.path.exists(docker_path) else local_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        placeholders = ','.join('?' for _ in watched_video_ids)
        cursor.execute(f'''
            SELECT primary_genre, secondary_genre, sub_genre, sub_sub_genre, COUNT(*) as count
            FROM video_genres
            WHERE video_id IN ({placeholders}) AND primary_genre IS NOT NULL
            GROUP BY primary_genre, secondary_genre, sub_genre, sub_sub_genre
            ORDER BY count DESC
        ''', watched_video_ids)

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

def create_dynamic_genre_tree():
    """Create genre tree from actual database genre data"""
    try:
        conn = sqlite3.connect('/app/data/youtube_videos.db')
        cursor = conn.cursor()

        # Get genre hierarchy from database with counts
        cursor.execute('''
            SELECT
                vg.primary_genre,
                vg.secondary_genre,
                vg.sub_genre,
                COUNT(*) as count
            FROM video_genres vg
            WHERE vg.primary_genre IS NOT NULL
            GROUP BY vg.primary_genre, vg.secondary_genre, vg.sub_genre
            ORDER BY vg.primary_genre, count DESC
        ''')

        results = cursor.fetchall()
        conn.close()

        # Build hierarchical structure
        genre_hierarchy = {}
        total_videos = len(results)

        for primary, secondary, sub, count in results:
            if primary not in genre_hierarchy:
                genre_hierarchy[primary] = {
                    'count': 0,
                    'children': {}
                }

            genre_hierarchy[primary]['count'] += count

            if secondary:
                if secondary not in genre_hierarchy[primary]['children']:
                    genre_hierarchy[primary]['children'][secondary] = {
                        'count': 0,
                        'children': {}
                    }
                genre_hierarchy[primary]['children'][secondary]['count'] += count

                if sub:
                    if sub not in genre_hierarchy[primary]['children'][secondary]['children']:
                        genre_hierarchy[primary]['children'][secondary]['children'][sub] = {
                            'count': 0
                        }
                    genre_hierarchy[primary]['children'][secondary]['children'][sub]['count'] += count

        # Convert to genre tree format, limit to top 3 primary genres
        genre_tree = []
        for primary_name, primary_data in sorted(genre_hierarchy.items(),
                                                key=lambda x: x[1]['count'], reverse=True)[:3]:

            # Build secondary children (limit to top 4)
            secondary_children = []
            for sec_name, sec_data in sorted(primary_data['children'].items(),
                                           key=lambda x: x[1]['count'], reverse=True)[:4]:

                # Build sub children (limit to top 3)
                sub_children = []
                for sub_name, sub_data in sorted(sec_data['children'].items(),
                                               key=lambda x: x[1]['count'], reverse=True)[:3]:
                    sub_children.append({
                        'id': f"{primary_name}_{sec_name}_{sub_name}".lower().replace(' ', '_').replace('&', 'and'),
                        'name': sub_name,
                        'level': 3,
                        'path': [primary_name, sec_name, sub_name]
                    })

                secondary_children.append({
                    'id': f"{primary_name}_{sec_name}".lower().replace(' ', '_').replace('&', 'and'),
                    'name': sec_name,
                    'level': 2,
                    'path': [primary_name, sec_name],
                    'children': sub_children if sub_children else None
                })

            genre_tree.append({
                'id': primary_name.lower().replace(' ', '_').replace('&', 'and'),
                'name': primary_name,
                'level': 1,
                'path': [primary_name],
                'children': secondary_children if secondary_children else None
            })

        return genre_tree

    except Exception as e:
        print(f"Error creating dynamic genre tree: {e}")
        return create_fallback_genre_tree()

def create_fallback_genre_tree():
    """Create a fallback genre tree from channels and basic categorization"""
    if not watch_history_data:
        return []

    # Create simple tree based on top channels
    channel_counts = Counter()
    for video in watch_history_data['watch_history']:
        channel = video.get('channel', '')
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
    # Load watch history directly for this endpoint to ensure we have data
    try:
        with open('/app/youtube_watch_history.json', 'r') as file:
            current_watch_history = json.load(file)
    except Exception as e:
        print(f"Error loading watch history in profile endpoint: {e}")
        current_watch_history = {"watch_history": []}

    top_channels = analyze_top_channels()
    genre_percentages = analyze_genre_percentages()
    # Check for force_new parameter
    force_new = request.args.get('force_new', 'false').lower() == 'true'
    # Create hardcoded genre tree with actual database genre names
    genre_tree = []

    if current_watch_history and current_watch_history.get('watch_history'):
        from collections import Counter

        channel_counts = Counter()
        for video in current_watch_history['watch_history']:
            channel = video.get('channel', '')
            if channel:
                channel_counts[channel] += 1

        total_videos = len(current_watch_history['watch_history'])

        # Education category
        edu_channels = ['Veritasium', 'Kurzgesagt – In a Nutshell', 'TED', 'CrashCourse', 'AsapSCIENCE']
        edu_count = sum(count for channel, count in channel_counts.items()
                       if any(edu_ch in channel for edu_ch in edu_channels))

        if edu_count > 0:
            genre_tree.append({
                'id': 'education',
                'name': 'Education',
                'percentage': round((edu_count / total_videos) * 100),
                'level': 1,
                'path': ['Education'],
                'children': [
                    {
                        'id': 'education_science',
                        'name': 'Science',
                        'level': 2,
                        'path': ['Education', 'Science'],
                        'children': [
                            {'id': 'education_science_physics', 'name': 'Physics', 'level': 3, 'path': ['Education', 'Science', 'Physics']},
                            {'id': 'education_science_chemistry', 'name': 'Chemistry', 'level': 3, 'path': ['Education', 'Science', 'Chemistry']}
                        ]
                    }
                ]
            })

        # Technology category
        tech_channels = ['Marques Brownlee', 'Linus Tech Tips', 'TechLinked']
        tech_count = sum(count for channel, count in channel_counts.items()
                        if any(tech_ch in channel for tech_ch in tech_channels))

        if tech_count > 0:
            genre_tree.append({
                'id': 'technology',
                'name': 'Technology',
                'percentage': round((tech_count / total_videos) * 100),
                'level': 1,
                'path': ['Technology'],
                'children': [
                    {
                        'id': 'technology_gadgets',
                        'name': 'Gadgets',
                        'level': 2,
                        'path': ['Technology', 'Gadgets'],
                        'children': [
                            {'id': 'technology_gadgets_mobile', 'name': 'Mobile Devices', 'level': 3, 'path': ['Technology', 'Gadgets', 'Mobile Devices']},
                            {'id': 'technology_gadgets_audio', 'name': 'Audio Devices', 'level': 3, 'path': ['Technology', 'Gadgets', 'Audio Devices']}
                        ]
                    },
                    {
                        'id': 'technology_gaming',
                        'name': 'Gaming',
                        'level': 2,
                        'path': ['Technology', 'Gaming'],
                        'children': [
                            {'id': 'technology_gaming_hardware', 'name': 'Gaming Hardware', 'level': 3, 'path': ['Technology', 'Gaming', 'Gaming Hardware']},
                            {'id': 'technology_gaming_reviews', 'name': 'Game Reviews', 'level': 3, 'path': ['Technology', 'Gaming', 'Game Reviews']}
                        ]
                    },
                    {
                        'id': 'technology_news',
                        'name': 'Tech News',
                        'level': 2,
                        'path': ['Technology', 'Tech News'],
                        'children': []
                    }
                ]
            })

        # History category
        hist_channels = ['OverSimplified', 'CGP Grey']
        hist_count = sum(count for channel, count in channel_counts.items()
                        if any(hist_ch in channel for hist_ch in hist_channels))

        if hist_count > 0:
            genre_tree.append({
                'id': 'history',
                'name': 'News & Politics',
                'percentage': round((hist_count / total_videos) * 100),
                'level': 1,
                'path': ['News & Politics'],
                'children': [
                    {
                        'id': 'history_wars',
                        'name': 'Wars & Conflicts',
                        'level': 2,
                        'path': ['News & Politics', 'Wars & Conflicts'],
                        'children': [
                            {'id': 'history_wars_ww2', 'name': 'World War II', 'level': 3, 'path': ['News & Politics', 'Wars & Conflicts', 'World War II']},
                            {'id': 'history_wars_coldwar', 'name': 'Cold War', 'level': 3, 'path': ['News & Politics', 'Wars & Conflicts', 'Cold War']}
                        ]
                    },
                    {
                        'id': 'history_civics',
                        'name': 'Politics & Civics',
                        'level': 2,
                        'path': ['News & Politics', 'Politics & Civics'],
                        'children': [
                            {'id': 'history_civics_government', 'name': 'Government Systems', 'level': 3, 'path': ['News & Politics', 'Politics & Civics', 'Government Systems']},
                            {'id': 'history_civics_geography', 'name': 'Political Geography', 'level': 3, 'path': ['News & Politics', 'Politics & Civics', 'Political Geography']}
                        ]
                    }
                ]
            })

    return jsonify({
        'topChannels': top_channels,
        'genrePercentages': genre_percentages,
        'genreTree': genre_tree,
        'totalVideos': len(current_watch_history['watch_history']) if current_watch_history else 0
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
            channel_match = search_query in video.get('channel', '').lower()

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

@app.route('/api/semantic-search', methods=['POST'])
def semantic_search():
    """Enhanced semantic search with genre context and chat log"""
    data = request.json

    # Extract search parameters
    query = data.get('query', '')
    genre_path = data.get('genrePath', [])
    chat_history = data.get('chatHistory', [])
    limit = data.get('limit', 20)

    try:
        # Use semantic search with genre context
        results = semantic_search_with_context(query, genre_path, chat_history, limit)

        return jsonify({
            'videos': results,
            'total': len(results),
            'query': query,
            'genrePath': genre_path,
            'searchExplanation': generate_search_explanation(query, genre_path, len(results))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def semantic_search_with_context(query: str, genre_path: list, chat_history: list, limit: int = 20):
    """Perform semantic search using OpenAI embeddings with genre context"""
    import openai
    import numpy as np

    if not query.strip():
        return []

    try:
        # Install scikit-learn for similarity calculation
        try:
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
            print("Installing scikit-learn for similarity calculation...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
            from sklearn.metrics.pairwise import cosine_similarity

        # Get videos from database with genre filtering
        # Use the same path logic as load_watch_history
        docker_path = '/app/data/youtube_videos.db'
        local_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')
        db_path = docker_path if os.path.exists(docker_path) else local_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        base_query = '''
            SELECT v.video_id, v.title, v.channel_title, v.description,
                   v.thumbnail, v.duration, v.view_count, v.like_count,
                   v.published_at, v.tags, v.categories,
                   vg.primary_genre, vg.secondary_genre, vg.sub_genre,
                   vg.content_type, vg.educational_level, vg.target_audience
            FROM videos v
            LEFT JOIN (
                SELECT video_id,
                       MAX(primary_genre) as primary_genre,
                       MAX(secondary_genre) as secondary_genre,
                       MAX(sub_genre) as sub_genre,
                       MAX(content_type) as content_type,
                       MAX(educational_level) as educational_level,
                       MAX(target_audience) as target_audience
                FROM video_genres
                GROUP BY video_id
            ) vg ON v.video_id = vg.video_id
        '''

        # Add genre filtering if provided
        where_clauses = []
        if genre_path:
            if len(genre_path) >= 1:
                where_clauses.append(f"vg.primary_genre = '{genre_path[0]}'")
            if len(genre_path) >= 2:
                where_clauses.append(f"vg.secondary_genre = '{genre_path[1]}'")

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        base_query += " ORDER BY v.view_count DESC LIMIT 100"

        cursor.execute(base_query)
        videos = cursor.fetchall()
        conn.close()

        if not videos:
            return keyword_fallback_search(query, genre_path, limit)

        # Prepare search context
        search_context = f"User query: {query}"
        if genre_path:
            search_context += f"\\nGenre context: {' → '.join(genre_path)}"

        # Create query embedding
        openai.api_key = os.getenv('OPENAI_API_KEY')
        query_response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=search_context
        )
        query_embedding = np.array(query_response.data[0].embedding)

        # Score videos by semantic similarity
        scored_videos = []
        for video_data in videos:
            # Create video text for embedding
            video_text = f"Title: {video_data[1] or ''}"
            if video_data[3]:  # description
                video_text += f" Description: {video_data[3][:300]}"
            if video_data[9]:  # tags
                try:
                    tags = json.loads(video_data[9]) if isinstance(video_data[9], str) else video_data[9]
                    if tags:
                        video_text += f" Tags: {', '.join(tags[:8])}"
                except:
                    pass

            # Get video embedding
            video_response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=video_text
            )
            video_embedding = np.array(video_response.data[0].embedding)

            # Calculate similarity
            similarity = cosine_similarity([query_embedding], [video_embedding])[0][0]

            if similarity > 0.25:  # Threshold filter
                video_dict = format_video_for_search(video_data, similarity)
                scored_videos.append(video_dict)

        # Sort by similarity and return
        scored_videos.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_videos[:limit]

    except Exception as e:
        print(f"Semantic search error: {e}")
        return keyword_fallback_search(query, genre_path, limit)

def keyword_fallback_search(query: str, genre_path: list, limit: int):
    """Fallback keyword search"""
    try:
        # Use the same path logic as load_watch_history
        docker_path = '/app/data/youtube_videos.db'
        local_path = os.path.join(os.path.dirname(__file__), 'youtube_videos.db')
        db_path = docker_path if os.path.exists(docker_path) else local_path
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        search_query = '''
            SELECT v.video_id, v.title, v.channel_title, v.description,
                   v.thumbnail, v.duration, v.view_count, v.like_count,
                   v.published_at, v.tags, v.categories,
                   vg.primary_genre, vg.secondary_genre, vg.sub_genre,
                   vg.content_type, vg.educational_level, vg.target_audience
            FROM videos v
            LEFT JOIN video_genres vg ON v.video_id = vg.video_id
            WHERE (v.title LIKE ? OR v.description LIKE ?)
        '''

        params = [f'%{query}%', f'%{query}%']
        if genre_path and len(genre_path) >= 1:
            search_query += " AND vg.primary_genre = ?"
            params.append(genre_path[0])

        search_query += f" ORDER BY v.view_count DESC LIMIT {limit}"
        cursor.execute(search_query, params)
        videos = cursor.fetchall()
        conn.close()

        return [format_video_for_search(video_data, 0.5) for video_data in videos]

    except Exception as e:
        print(f"Fallback search error: {e}")
        return []

def format_video_for_search(video_data: tuple, similarity_score: float) -> dict:
    """Format video data for search results"""
    (video_id, title, channel_title, description, thumbnail, duration,
     view_count, like_count, published_at, tags, categories,
     primary_genre, secondary_genre, sub_genre, content_type,
     educational_level, target_audience) = video_data

    # Parse tags
    parsed_tags = []
    if tags:
        try:
            parsed_tags = json.loads(tags) if isinstance(tags, str) else tags
        except:
            parsed_tags = []

    return {
        'video_id': video_id,
        'title': title,
        'channel': channel_title,
        'description': description or '',
        'thumbnail': thumbnail or '',
        'duration': duration or 0,
        'view_count': view_count or 0,
        'like_count': like_count or 0,
        'published_at': published_at,
        'tags': parsed_tags,
        'categories': [categories] if categories else [],
        'similarity_score': round(similarity_score, 3),
        'genres': {
            'primary': primary_genre,
            'secondary': secondary_genre,
            'sub': sub_genre,
            'content_type': content_type,
            'educational_level': educational_level,
            'target_audience': target_audience
        }
    }

def generate_search_explanation(query: str, genre_path: list, result_count: int) -> str:
    """Generate explanation of search results"""
    explanation = f"Found {result_count} videos"
    if query:
        explanation += f" matching '{query}'"
    if genre_path:
        explanation += f" in {' → '.join(genre_path)}"
    explanation += " using semantic similarity search"
    return explanation

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'videos_loaded': len(watch_history_data['watch_history']) if watch_history_data else 0
    })

@app.route('/api/test-genre', methods=['GET'])
def test_genre():
    """Test endpoint for genre tree generation"""
    import json
    from collections import Counter

    try:
        with open('/app/youtube_watch_history.json', 'r') as file:
            current_watch_history = json.load(file)
    except Exception as e:
        return jsonify({'error': f'Error loading watch history: {e}'})

    if not current_watch_history or not current_watch_history.get('watch_history'):
        return jsonify({'error': 'No watch history found'})

    channel_counts = Counter()
    for video in current_watch_history['watch_history']:
        channel = video.get('channel', '')
        if channel:
            channel_counts[channel] += 1

    total_videos = len(current_watch_history['watch_history'])

    # Education category
    edu_channels = ['Veritasium', 'Kurzgesagt – In a Nutshell', 'TED', 'CrashCourse', 'AsapSCIENCE']
    edu_count = sum(count for channel, count in channel_counts.items()
                   if any(edu_ch in channel for edu_ch in edu_channels))

    genre_tree = []
    if edu_count > 0:
        genre_tree.append({
            'id': 'education',
            'name': 'Education',
            'percentage': round((edu_count / total_videos) * 100),
            'level': 1,
            'path': ['Education'],
            'children': [
                {
                    'id': 'education_science',
                    'name': 'Science',
                    'level': 2,
                    'path': ['Education', 'Science'],
                    'children': [
                        {'id': 'education_science_physics', 'name': 'Physics', 'level': 3, 'path': ['Education', 'Science', 'Physics']},
                        {'id': 'education_science_chemistry', 'name': 'Chemistry', 'level': 3, 'path': ['Education', 'Science', 'Chemistry']}
                    ]
                }
            ]
        })

    return jsonify({
        'success': True,
        'total_videos': total_videos,
        'edu_count': edu_count,
        'genre_tree': genre_tree,
        'channel_counts': dict(channel_counts)
    })

if __name__ == '__main__':
    # Load watch history on startup
    load_watch_history()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
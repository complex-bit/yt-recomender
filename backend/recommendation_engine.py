#!/usr/bin/env python3
"""
YouTube Video Recommendation Engine
Uses genre classifications and watch history to recommend videos
"""

import sqlite3
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class RecommendationEngine:
    def __init__(self, db_path: str, watch_history_path: str):
        self.db_path = db_path
        self.watch_history_path = watch_history_path
        self.user_preferences = None
        self.watched_video_ids = set()

    def load_user_preferences(self) -> Dict:
        """Load and analyze user watch history to build preference profile"""
        try:
            with open(self.watch_history_path, 'r') as f:
                history_data = json.load(f)

            watch_history = history_data.get('watch_history', [])
            self.watched_video_ids = {v.get('video_id') for v in watch_history}

            # Calculate preferences based on watch history
            preferences = self._calculate_user_preferences(watch_history)
            self.user_preferences = preferences

            return preferences

        except Exception as e:
            print(f"Error loading user preferences: {e}")
            return {}

    def _calculate_user_preferences(self, watch_history: List[Dict]) -> Dict:
        """Analyze watch history to extract user preferences"""
        genre_scores = defaultdict(float)
        channel_scores = defaultdict(float)
        educational_levels = []
        total_watch_time = 0
        completion_rates = []

        for video in watch_history:
            watch_time = video.get('watch_time_seconds', 0)
            total_watch_time += watch_time

            # Calculate completion rate (assuming average video is 600 seconds)
            estimated_duration = 600  # fallback
            completion_rate = min(watch_time / estimated_duration, 1.0)
            completion_rates.append(completion_rate)

            # Score based on watch time (longer watch time = higher preference)
            time_weight = min(watch_time / 300, 3.0)  # Cap at 3x weight

            # Get genres for this video from database
            video_id = video.get('video_id')
            if video_id:
                genres = self._get_video_genres(video_id)
                for genre_type, genre_value in genres.items():
                    if genre_value:
                        genre_scores[f"{genre_type}:{genre_value}"] += time_weight

            # Channel preferences
            channel = video.get('channel')
            if channel:
                channel_scores[channel] += time_weight

        # Normalize scores
        total_genre_score = sum(genre_scores.values()) or 1
        total_channel_score = sum(channel_scores.values()) or 1

        normalized_genres = {k: v/total_genre_score for k, v in genre_scores.items()}
        normalized_channels = {k: v/total_channel_score for k, v in channel_scores.items()}

        avg_completion = np.mean(completion_rates) if completion_rates else 0.5

        return {
            'genre_preferences': normalized_genres,
            'channel_preferences': normalized_channels,
            'avg_completion_rate': avg_completion,
            'total_watch_time': total_watch_time,
            'video_count': len(watch_history)
        }

    def _get_video_genres(self, video_id: str) -> Dict:
        """Get genre classification for a video"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT primary_genre, secondary_genre, sub_genre,
                       content_type, educational_level, target_audience
                FROM video_genres WHERE video_id = ?
            ''', (video_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'primary_genre': result[0],
                    'secondary_genre': result[1],
                    'sub_genre': result[2],
                    'content_type': result[3],
                    'educational_level': result[4],
                    'target_audience': result[5]
                }
            return {}

        except Exception as e:
            print(f"Error getting video genres: {e}")
            return {}

    def get_recommendations(self, limit: int = 20, filters: Dict = None) -> List[Dict]:
        """Generate personalized video recommendations"""
        if not self.user_preferences:
            self.load_user_preferences()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all videos with their genres, excluding already watched
            placeholders = ','.join('?' for _ in self.watched_video_ids) if self.watched_video_ids else "''"

            query = f'''
                SELECT DISTINCT v.video_id, v.title, v.channel_title, v.description,
                       v.thumbnail, v.duration, v.view_count, v.like_count,
                       v.published_at, v.tags, v.categories,
                       vg.primary_genre, vg.secondary_genre, vg.sub_genre,
                       vg.content_type, vg.educational_level, vg.target_audience,
                       vg.confidence_score
                FROM videos v
                LEFT JOIN (
                    SELECT video_id,
                           MAX(primary_genre) as primary_genre,
                           MAX(secondary_genre) as secondary_genre,
                           MAX(sub_genre) as sub_genre,
                           MAX(content_type) as content_type,
                           MAX(educational_level) as educational_level,
                           MAX(target_audience) as target_audience,
                           AVG(confidence_score) as confidence_score
                    FROM video_genres
                    GROUP BY video_id
                ) vg ON v.video_id = vg.video_id
                WHERE v.video_id NOT IN ({placeholders})
                ORDER BY v.view_count DESC
                LIMIT 100
            '''

            if self.watched_video_ids:
                cursor.execute(query, tuple(self.watched_video_ids))
            else:
                cursor.execute(query.replace(f"NOT IN ({placeholders})", "NOT IN ('')"))

            videos = cursor.fetchall()
            conn.close()

            # Score and rank videos
            scored_videos = []
            for video in videos:
                score = self._calculate_video_score(video)
                if score > 0:  # Only include videos with positive scores
                    video_dict = self._format_video_dict(video, score)
                    scored_videos.append(video_dict)

            # Sort by score and apply filters
            scored_videos.sort(key=lambda x: x['recommendation_score'], reverse=True)

            if filters:
                scored_videos = self._apply_filters(scored_videos, filters)

            return scored_videos[:limit]

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []

    def _calculate_video_score(self, video_data: Tuple) -> float:
        """Calculate recommendation score for a video"""
        if not self.user_preferences:
            return 0.0

        (video_id, title, channel_title, description, thumbnail, duration,
         view_count, like_count, published_at, tags, categories,
         primary_genre, secondary_genre, sub_genre, content_type,
         educational_level, target_audience, confidence_score) = video_data

        score = 0.0
        genre_prefs = self.user_preferences.get('genre_preferences', {})
        channel_prefs = self.user_preferences.get('channel_preferences', {})

        # Genre matching score (40% of total score)
        if primary_genre:
            score += genre_prefs.get(f'primary_genre:{primary_genre}', 0) * 0.4
        if secondary_genre:
            score += genre_prefs.get(f'secondary_genre:{secondary_genre}', 0) * 0.25
        if sub_genre:
            score += genre_prefs.get(f'sub_genre:{sub_genre}', 0) * 0.15

        # Channel preference score (30% of total score)
        if channel_title:
            score += channel_prefs.get(channel_title, 0) * 0.3

        # Content type matching (10% of total score)
        if content_type:
            score += genre_prefs.get(f'content_type:{content_type}', 0) * 0.1

        # Educational level matching (10% of total score)
        if educational_level:
            score += genre_prefs.get(f'educational_level:{educational_level}', 0) * 0.1

        # Popularity boost (10% of total score)
        if view_count and view_count > 0:
            # Normalize view count and add small boost
            popularity_score = min(np.log10(view_count) / 10, 0.1)
            score += popularity_score

        # Confidence penalty for low-confidence classifications
        if confidence_score and confidence_score < 0.7:
            score *= confidence_score

        return score

    def _format_video_dict(self, video_data: Tuple, score: float) -> Dict:
        """Format video data into dictionary"""
        (video_id, title, channel_title, description, thumbnail, duration,
         view_count, like_count, published_at, tags, categories,
         primary_genre, secondary_genre, sub_genre, content_type,
         educational_level, target_audience, confidence_score) = video_data

        # Parse tags if they're JSON string
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
            'recommendation_score': round(score, 3),
            'match_reasons': self._get_match_reasons(video_data, score),
            'genres': {
                'primary': primary_genre,
                'secondary': secondary_genre,
                'sub': sub_genre,
                'content_type': content_type,
                'educational_level': educational_level,
                'target_audience': target_audience
            }
        }

    def _get_match_reasons(self, video_data: Tuple, score: float) -> List[str]:
        """Generate human-readable reasons why this video was recommended"""
        reasons = []
        (_, title, channel_title, _, _, _, _, _, _, _, _,
         primary_genre, secondary_genre, sub_genre, content_type,
         educational_level, target_audience, confidence_score) = video_data

        channel_prefs = self.user_preferences.get('channel_preferences', {})

        if channel_title and channel_prefs.get(channel_title, 0) > 0.1:
            reasons.append(f"You enjoy {channel_title} videos")

        if primary_genre:
            reasons.append(f"Matches your interest in {primary_genre}")

        if sub_genre:
            reasons.append(f"Related to {sub_genre}")

        if score > 0.5:
            reasons.append("Highly recommended for you")

        return reasons[:3]  # Limit to 3 reasons

    def _apply_filters(self, videos: List[Dict], filters: Dict) -> List[Dict]:
        """Apply user-specified filters to recommendations"""
        filtered_videos = videos

        # Educational level filter
        if 'educational_level' in filters:
            level = filters['educational_level']
            filtered_videos = [v for v in filtered_videos
                             if v.get('genres', {}).get('educational_level') == level]

        # Duration filter
        if 'min_duration' in filters:
            min_dur = filters['min_duration']
            filtered_videos = [v for v in filtered_videos if v.get('duration', 0) >= min_dur]

        if 'max_duration' in filters:
            max_dur = filters['max_duration']
            filtered_videos = [v for v in filtered_videos if v.get('duration', 0) <= max_dur]

        # Channel filter
        if 'channels' in filters:
            allowed_channels = filters['channels']
            filtered_videos = [v for v in filtered_videos
                             if v.get('channel') in allowed_channels]

        # Genre path filter (from genre wheel selection)
        if 'genre_path' in filters and filters['genre_path']:
            genre_path = filters['genre_path']
            if len(genre_path) >= 1:  # Primary genre
                filtered_videos = [v for v in filtered_videos
                                 if v.get('genres', {}).get('primary') == genre_path[0]]
            if len(genre_path) >= 2:  # Secondary genre
                filtered_videos = [v for v in filtered_videos
                                 if v.get('genres', {}).get('secondary') == genre_path[1]]
            if len(genre_path) >= 3:  # Sub genre
                filtered_videos = [v for v in filtered_videos
                                 if v.get('genres', {}).get('sub') == genre_path[2]]

        # Popularity filter (0-100 slider)
        if 'popularity' in filters:
            popularity_val = filters['popularity']
            if popularity_val < 30:  # Hidden gems (low views)
                filtered_videos = [v for v in filtered_videos if v.get('view_count', 0) < 100000]
            elif popularity_val > 70:  # Popular hits (high views)
                filtered_videos = [v for v in filtered_videos if v.get('view_count', 0) > 1000000]
            # Middle range (30-70) shows all

        # Recency filter (0-100 slider)
        if 'recency' in filters:
            from datetime import datetime, timedelta
            recency_val = filters['recency']

            # Sort by published date and filter
            try:
                videos_with_dates = []
                for v in filtered_videos:
                    if v.get('published_at'):
                        try:
                            # Parse ISO date
                            pub_date = datetime.fromisoformat(v['published_at'].replace('Z', '+00:00'))
                            videos_with_dates.append((v, pub_date))
                        except:
                            videos_with_dates.append((v, datetime.min))
                    else:
                        videos_with_dates.append((v, datetime.min))

                # Sort by date
                videos_with_dates.sort(key=lambda x: x[1], reverse=True)

                if recency_val < 30:  # Classic videos (older)
                    # Take bottom 70% (older videos)
                    start_idx = int(len(videos_with_dates) * 0.3)
                    filtered_videos = [v[0] for v in videos_with_dates[start_idx:]]
                elif recency_val > 70:  # Fresh videos (newer)
                    # Take top 30% (newer videos)
                    end_idx = int(len(videos_with_dates) * 0.3)
                    filtered_videos = [v[0] for v in videos_with_dates[:end_idx]]
                else:
                    # Middle range shows all
                    filtered_videos = [v[0] for v in videos_with_dates]
            except:
                # If date parsing fails, keep original list
                pass

        # Uniqueness filter (0-100 slider)
        if 'uniqueness' in filters:
            uniqueness_val = filters['uniqueness']
            user_channels = set(self.user_preferences.get('channel_preferences', {}).keys())

            if uniqueness_val < 30:  # Familiar channels (channels you've watched)
                filtered_videos = [v for v in filtered_videos
                                 if v.get('channel') in user_channels]
            elif uniqueness_val > 70:  # New channels (channels you haven't watched)
                filtered_videos = [v for v in filtered_videos
                                 if v.get('channel') not in user_channels]
            # Middle range (30-70) shows mix of both

        return filtered_videos

    def get_user_analytics(self) -> Dict:
        """Get analytics about user's viewing patterns"""
        if not self.user_preferences:
            self.load_user_preferences()

        genre_prefs = self.user_preferences.get('genre_preferences', {})
        channel_prefs = self.user_preferences.get('channel_preferences', {})

        # Group preferences by type
        analytics = {
            'top_genres': {},
            'top_channels': dict(list(sorted(channel_prefs.items(),
                                           key=lambda x: x[1], reverse=True))[:5]),
            'completion_rate': self.user_preferences.get('avg_completion_rate', 0),
            'total_watch_time': self.user_preferences.get('total_watch_time', 0),
            'video_count': self.user_preferences.get('video_count', 0)
        }

        # Extract top genres by type
        for pref_key, score in genre_prefs.items():
            if ':' in pref_key:
                genre_type, genre_value = pref_key.split(':', 1)
                if genre_type not in analytics['top_genres']:
                    analytics['top_genres'][genre_type] = {}
                analytics['top_genres'][genre_type][genre_value] = score

        # Keep only top 3 for each genre type
        for genre_type in analytics['top_genres']:
            analytics['top_genres'][genre_type] = dict(
                list(sorted(analytics['top_genres'][genre_type].items(),
                           key=lambda x: x[1], reverse=True))[:3]
            )

        return analytics
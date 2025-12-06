#!/usr/bin/env python3
"""
Test script to verify genre tree generation works
"""

import json
from collections import Counter

def generate_simple_genre_tree():
    """Generate a simple genre tree for testing"""
    try:
        with open('youtube_watch_history.json', 'r') as file:
            current_watch_history = json.load(file)
    except Exception as e:
        print(f"Error loading watch history: {e}")
        return []

    if not current_watch_history or not current_watch_history.get('watch_history'):
        print("No watch history found")
        return []

    print(f"Loaded {len(current_watch_history['watch_history'])} videos")

    channel_counts = Counter()
    for video in current_watch_history['watch_history']:
        channel = video.get('channel') or video.get('channelTitle')
        if channel:
            channel_counts[channel] += 1

    total_videos = len(current_watch_history['watch_history'])
    print(f"Total videos: {total_videos}")

    # Education category
    edu_channels = ['Veritasium', 'Kurzgesagt – In a Nutshell', 'TED', 'CrashCourse', 'AsapSCIENCE']
    edu_count = sum(count for channel, count in channel_counts.items()
                   if any(edu_ch in channel for edu_ch in edu_channels))

    # Technology category
    tech_channels = ['Marques Brownlee', 'Linus Tech Tips', 'TechLinked']
    tech_count = sum(count for channel, count in channel_counts.items()
                    if any(tech_ch in channel for tech_ch in tech_channels))

    # History category
    hist_channels = ['OverSimplified', 'CGP Grey']
    hist_count = sum(count for channel, count in channel_counts.items()
                    if any(hist_ch in channel for hist_ch in hist_channels))

    print(f"Education count: {edu_count}")
    print(f"Technology count: {tech_count}")
    print(f"History count: {hist_count}")

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

    if tech_count > 0:
        genre_tree.append({
            'id': 'technology',
            'name': 'Technology',
            'percentage': round((tech_count / total_videos) * 100),
            'level': 1,
            'path': ['Technology'],
            'children': [
                {
                    'id': 'technology_reviews',
                    'name': 'Reviews',
                    'level': 2,
                    'path': ['Technology', 'Reviews'],
                    'children': []
                }
            ]
        })

    if hist_count > 0:
        genre_tree.append({
            'id': 'history',
            'name': 'History & Politics',
            'percentage': round((hist_count / total_videos) * 100),
            'level': 1,
            'path': ['History & Politics'],
            'children': []
        })

    return genre_tree

if __name__ == "__main__":
    result = generate_simple_genre_tree()
    print(f"Generated genre tree with {len(result)} categories:")
    for genre in result:
        print(f"  • {genre['name']} ({genre.get('percentage', 0)}%)")
    print("\nFull JSON:")
    print(json.dumps(result, indent=2))
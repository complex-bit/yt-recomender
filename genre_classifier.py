#!/usr/bin/env python3
"""
Genre Classification System for YouTube Videos
Analyzes video descriptions using GPT API to extract detailed genre classifications
"""

import sqlite3
import json
import os
import time
from typing import Dict, List, Optional
import requests

class GenreClassifier:
    def __init__(self, db_path: str, api_key: str):
        self.db_path = db_path
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def create_genre_tables(self):
        """Create tables for storing genre classifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main genres table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                primary_genre TEXT NOT NULL,
                secondary_genre TEXT,
                sub_genre TEXT,
                sub_sub_genre TEXT,
                content_type TEXT,
                educational_level TEXT,
                target_audience TEXT,
                confidence_score REAL,
                analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
        ''')

        # Genre hierarchy reference table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genre_hierarchy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                primary_genre TEXT,
                secondary_genre TEXT,
                sub_genre TEXT,
                description TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print("Genre tables created successfully")

    def get_genre_prompt(self, title: str, description: str, tags: str) -> str:
        """Create a detailed prompt for genre classification"""
        return f"""
Analyze this YouTube video and classify it into detailed genres. Return a JSON object with the following structure:

{{
    "primary_genre": "main category (e.g., Education, Entertainment, Technology)",
    "secondary_genre": "more specific category (e.g., Science, Gaming, Tutorial)",
    "sub_genre": "detailed subcategory (e.g., Physics, FPS Games, Programming)",
    "sub_sub_genre": "very specific niche (e.g., Quantum Physics, Battle Royale, Web Development)",
    "content_type": "format type (e.g., Explanation, Review, Tutorial, Documentary, Comedy)",
    "educational_level": "complexity (e.g., Beginner, Intermediate, Advanced, Academic)",
    "target_audience": "intended viewers (e.g., General Public, Students, Professionals, Children)",
    "confidence_score": 0.95
}}

Video Data:
Title: {title}
Description: {description[:500]}...
Tags: {tags}

Focus on accuracy and be specific with sub-categories. Consider the educational value, entertainment factor, and technical complexity.
"""

    def classify_video(self, title: str, description: str, tags: str) -> Optional[Dict]:
        """Call GPT API to classify a single video"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert content curator who specializes in categorizing YouTube videos into detailed genre hierarchies. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": self.get_genre_prompt(title, description, tags)
                }
            ],
            "temperature": 0.3,
            "max_tokens": 300
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            # Parse JSON response
            genre_data = json.loads(content)
            return genre_data

        except Exception as e:
            print(f"Error classifying video '{title[:30]}...': {e}")
            return None

    def save_genre_classification(self, video_id: str, genre_data: Dict):
        """Save genre classification to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO video_genres
            (video_id, primary_genre, secondary_genre, sub_genre, sub_sub_genre,
             content_type, educational_level, target_audience, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_id,
            genre_data.get('primary_genre'),
            genre_data.get('secondary_genre'),
            genre_data.get('sub_genre'),
            genre_data.get('sub_sub_genre'),
            genre_data.get('content_type'),
            genre_data.get('educational_level'),
            genre_data.get('target_audience'),
            genre_data.get('confidence_score', 0.0)
        ))

        conn.commit()
        conn.close()

    def process_videos_batch(self, batch_size: int = 10, start_from: int = 0):
        """Process videos in batches to avoid API rate limits"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get videos that haven't been processed yet
        cursor.execute('''
            SELECT v.video_id, v.title, v.description, v.tags
            FROM videos v
            LEFT JOIN video_genres vg ON v.video_id = vg.video_id
            WHERE vg.video_id IS NULL
            LIMIT ? OFFSET ?
        ''', (batch_size, start_from))

        videos = cursor.fetchall()
        conn.close()

        if not videos:
            print("No more videos to process")
            return False

        print(f"Processing {len(videos)} videos...")

        for i, (video_id, title, description, tags) in enumerate(videos):
            print(f"Processing {i+1}/{len(videos)}: {title[:50]}...")

            genre_data = self.classify_video(title, description or "", tags or "")

            if genre_data:
                self.save_genre_classification(video_id, genre_data)
                print(f"  -> {genre_data.get('primary_genre')} > {genre_data.get('secondary_genre')}")

            # Rate limiting - wait between requests
            time.sleep(1)

        return len(videos) == batch_size  # True if there might be more videos

    def get_genre_statistics(self):
        """Get statistics about classified genres"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT primary_genre, COUNT(*) as count
            FROM video_genres
            GROUP BY primary_genre
            ORDER BY count DESC
        ''')

        primary_stats = cursor.fetchall()

        cursor.execute('''
            SELECT primary_genre, secondary_genre, COUNT(*) as count
            FROM video_genres
            WHERE secondary_genre IS NOT NULL
            GROUP BY primary_genre, secondary_genre
            ORDER BY count DESC
        ''')

        secondary_stats = cursor.fetchall()

        conn.close()

        return {
            "primary_genres": primary_stats,
            "secondary_genres": secondary_stats[:20]  # Top 20
        }

def main():
    # Configuration
    DB_PATH = "backend/youtube_videos.db"
    API_KEY = os.getenv("OPENAI_API_KEY")

    if not API_KEY:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        return

    classifier = GenreClassifier(DB_PATH, API_KEY)

    # Create tables
    classifier.create_genre_tables()

    # Process videos in batches
    batch_num = 0
    while True:
        print(f"\n--- Processing batch {batch_num + 1} ---")
        has_more = classifier.process_videos_batch(batch_size=5, start_from=batch_num * 5)

        if not has_more:
            break

        batch_num += 1

        # Show progress
        stats = classifier.get_genre_statistics()
        print(f"\nCurrent stats: {len(stats['primary_genres'])} primary genres found")
        for genre, count in stats['primary_genres'][:5]:
            print(f"  {genre}: {count} videos")

    # Final statistics
    print("\n=== Final Genre Statistics ===")
    stats = classifier.get_genre_statistics()

    print(f"\nPrimary Genres ({len(stats['primary_genres'])} total):")
    for genre, count in stats['primary_genres']:
        print(f"  {genre}: {count} videos")

    print(f"\nTop Secondary Genres:")
    for primary, secondary, count in stats['secondary_genres']:
        print(f"  {primary} > {secondary}: {count} videos")

if __name__ == "__main__":
    main()
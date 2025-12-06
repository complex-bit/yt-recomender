#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
sys.path.append('/home/alex/code/pp/yt-recomender/backend')

from recommendation_engine import RecommendationEngine
import json

# Initialize recommendation engine
engine = RecommendationEngine('/app/data/youtube_videos.db', '/app/youtube_watch_history.json')

print("=== Checking raw SQL query results ===")
import sqlite3
conn = sqlite3.connect('/app/data/youtube_videos.db')
cursor = conn.cursor()

# Get same query as recommendation engine
query = '''
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
    WHERE v.video_id NOT IN ('6akmv1bsz1M', 'idEAABFzpfg', '9scnWAgV6us', 'QDCcuCHOIyY', 'l4w6808wJcU', 'Ufmu1WD2TSk', 'h3M00JI8Iwo', 'g3FkuZNSGkw', '37Kn-kIsVu8', '_uk_6vfqwTA', 'd0lXrqjM_m8', 's1HA9LlFNM0', 'c7wCbbmLtiI', 'pCDY79Pl4TE', 'I-knioX60ug')
    ORDER BY
        CASE WHEN vg.primary_genre IS NOT NULL THEN 0 ELSE 1 END,
        v.view_count DESC
    LIMIT 100
'''

cursor.execute(query)
raw_results = cursor.fetchall()
print(f"Raw SQL returned {len(raw_results)} videos")

# Count by primary genre
from collections import Counter
raw_genres = [row[11] for row in raw_results if row[11]]  # primary_genre is index 11
genre_counts = Counter(raw_genres)
print("Raw genre counts:")
for genre, count in genre_counts.most_common():
    print(f"  {genre}: {count}")

print("\\nFirst few Technology videos from raw query:")
tech_videos = [row for row in raw_results if row[11] == 'Technology'][:3]
for i, row in enumerate(tech_videos):
    print(f"  {i+1}. {row[1][:50]}... | Channel: {row[2]}")

print("\\nChecking Technology video scoring:")
if tech_videos:
    sample_tech = tech_videos[0]
    score = engine._calculate_video_score(sample_tech)
    print(f"Sample Technology video score: {score}")
    print(f"  Title: {sample_tech[1]}")
    print(f"  Channel: {sample_tech[2]}")
    print(f"  Primary genre: {sample_tech[11]}")
else:
    print("No Technology videos found in first 100 results")

conn.close()

print("\\n=== Getting all recommendations ===")
all_recs = engine.get_recommendations(limit=5)
print(f"Total recommendations: {len(all_recs)}")
for i, rec in enumerate(all_recs[:3]):
    print(f"{i+1}. {rec['title'][:50]}... | Primary: '{rec['genres']['primary']}' | Score: {rec['recommendation_score']}")

print("\n=== Getting Technology recommendations ===")
tech_filters = {'genre_path': ['Technology']}
tech_recs = engine.get_recommendations(limit=5, filters=tech_filters)
print(f"Technology recommendations: {len(tech_recs)}")
for i, rec in enumerate(tech_recs[:3]):
    print(f"{i+1}. {rec['title'][:50]}... | Primary: '{rec['genres']['primary']}' | Score: {rec['recommendation_score']}")

print("\n=== Checking user preferences ===")
engine.load_user_preferences()
prefs = engine.user_preferences
print("Genre preferences:")
genre_prefs = prefs.get('genre_preferences', {})
for key, value in sorted(genre_prefs.items()):
    if 'primary_genre' in key and value > 0:
        print(f"  {key}: {value}")

print(f"\nTotal genre preferences: {len([k for k in genre_prefs.keys() if 'primary_genre' in k])}")

print("\n=== Checking all videos before filtering ===")
# Get unfiltered recommendations to see what primary genres exist
all_recs_big = engine.get_recommendations(limit=50)
primary_genres = [rec['genres']['primary'] for rec in all_recs_big]
unique_primaries = list(set(primary_genres))
print(f"Unique primary genres in recommendations: {sorted(unique_primaries)}")

# Count by primary genre
from collections import Counter
genre_counts = Counter(primary_genres)
print("Genre counts:")
for genre, count in genre_counts.most_common():
    print(f"  {genre}: {count}")
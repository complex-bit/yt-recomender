#!/usr/bin/env python3
"""
Script to check progress of part 2 database scraping
"""

import sqlite3
import os

def check_progress():
    db_file = 'youtube_videos_part2.db'

    if not os.path.exists(db_file):
        print("Part 2 database not yet created")
        return

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check total videos
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]

        # Check unique channels
        cursor.execute("SELECT COUNT(DISTINCT channel_id) FROM videos")
        unique_channels = cursor.fetchone()[0]

        # Check most recent video
        cursor.execute("SELECT MAX(scraped_at) FROM videos")
        last_scraped = cursor.fetchone()[0]

        print(f"Part 2 Database Progress:")
        print(f"  Total videos: {total_videos}")
        print(f"  Unique channels: {unique_channels}")
        print(f"  Last scraped: {last_scraped}")
        print(f"  Database size: {os.path.getsize(db_file) // 1024}KB")

        conn.close()

    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_progress()
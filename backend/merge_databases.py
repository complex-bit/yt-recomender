#!/usr/bin/env python3
"""
Script to merge part 2 database with main database
"""

import sqlite3
import os

def merge_databases():
    main_db = 'youtube_videos.db'
    part2_db = 'youtube_videos_part2.db'
    backup_db = 'youtube_videos_backup.db'

    if not os.path.exists(part2_db):
        print("Part 2 database doesn't exist yet")
        return

    if not os.path.exists(main_db):
        print("Main database doesn't exist")
        return

    # Create backup first
    print("Creating backup of main database...")
    os.system(f"cp {main_db} {backup_db}")

    try:
        # Connect to both databases
        main_conn = sqlite3.connect(main_db)
        part2_conn = sqlite3.connect(part2_db)

        # Attach part2 database to main connection
        main_conn.execute(f"ATTACH DATABASE '{part2_db}' AS part2")

        # Insert videos from part2 that don't already exist in main
        main_conn.execute("""
            INSERT OR IGNORE INTO videos
            SELECT * FROM part2.videos
        """)

        # Insert channels from part2 that don't already exist in main
        main_conn.execute("""
            INSERT OR IGNORE INTO channels
            SELECT * FROM part2.channels
        """)

        main_conn.commit()

        # Check results
        cursor = main_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT channel_id) FROM videos")
        unique_channels = cursor.fetchone()[0]

        print(f"Merge complete!")
        print(f"  Total videos in merged database: {total_videos}")
        print(f"  Unique channels in merged database: {unique_channels}")

        main_conn.close()
        part2_conn.close()

    except Exception as e:
        print(f"Error during merge: {e}")
        # Restore backup if something went wrong
        if os.path.exists(backup_db):
            os.system(f"cp {backup_db} {main_db}")
            print("Restored backup due to error")

if __name__ == "__main__":
    merge_databases()
#!/usr/bin/env python3
"""
Example usage of the YouTube scraper

This script demonstrates how to use the YouTubeScraper class programmatically
"""

import os
from youtube_scraper import YouTubeScraper

def main():
    # You need to set your YouTube Data API key
    API_KEY = "YOUR_API_KEY_HERE"

    # Or get it from environment variable
    # API_KEY = os.getenv('YOUTUBE_API_KEY')

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your YouTube Data API key in this script or as environment variable YOUTUBE_API_KEY")
        return

    # Initialize the scraper
    scraper = YouTubeScraper(API_KEY)

    # List of popular engineering/educational channels
    channels = [
        {
            'name': 'Real Engineering',
            'url': 'https://www.youtube.com/@RealEngineering'
        },
        {
            'name': 'Veritasium',
            'url': 'https://www.youtube.com/@veritasium'
        },
        {
            'name': 'Kurzgesagt',
            'url': 'https://www.youtube.com/@kurzgesagt'
        },
        {
            'name': 'TED-Ed',
            'url': 'https://www.youtube.com/@TEDEd'
        },
        {
            'name': 'BBC Earth',
            'url': 'https://www.youtube.com/@BBCEarth'
        }
    ]

    print("Starting to scrape multiple channels...")
    print("=" * 50)

    success_count = 0

    for channel in channels:
        print(f"\nScraping {channel['name']}...")
        try:
            success = scraper.scrape_channel(channel['url'], max_videos=25)  # 25 videos per channel
            if success:
                success_count += 1
                print(f"✅ Successfully scraped {channel['name']}")
            else:
                print(f"❌ Failed to scrape {channel['name']}")
        except Exception as e:
            print(f"❌ Error scraping {channel['name']}: {e}")

    print("\n" + "=" * 50)
    print(f"Successfully scraped {success_count}/{len(channels)} channels")

    # Export all data to JSON
    print("\nExporting data to JSON...")
    scraper.export_to_json('scraped_channels_data.json')

    # Show some statistics
    import sqlite3
    conn = sqlite3.connect('youtube_videos.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM channels')
    channel_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM videos')
    video_count = cursor.fetchone()[0]

    cursor.execute('SELECT title, view_count, channel_title FROM videos ORDER BY view_count DESC LIMIT 5')
    top_videos = cursor.fetchall()

    print(f"\n📊 Database Statistics:")
    print(f"   Channels: {channel_count}")
    print(f"   Videos: {video_count}")

    print(f"\n🏆 Top 5 Most Viewed Videos:")
    for i, (title, views, channel) in enumerate(top_videos, 1):
        print(f"   {i}. {title[:50]}... ({views:,} views) - {channel}")

    conn.close()


if __name__ == '__main__':
    main()
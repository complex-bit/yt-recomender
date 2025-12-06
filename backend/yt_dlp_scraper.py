#!/usr/bin/env python3
"""
YouTube Channel Scraper using yt-dlp

This script scrapes YouTube channels using yt-dlp and stores the data in a database.
Much simpler than using the YouTube API - no API keys required!

Requirements:
- yt-dlp
- sqlite3 (built into Python)
"""

import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional
import re
import time

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp not installed")
    print("Install it with: pip install yt-dlp")
    sys.exit(1)

class YouTubeDLPScraper:
    def __init__(self, db_path: str = 'youtube_videos.db'):
        """Initialize the scraper with database path."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with videos table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,  -- Full video description
                channel_id TEXT NOT NULL,
                channel_title TEXT NOT NULL,
                channel_url TEXT,
                channel_subscriber_count INTEGER,
                published_at TEXT DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER DEFAULT 0,  -- in seconds
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                thumbnail TEXT,
                tags TEXT,  -- JSON string
                categories TEXT,  -- JSON string
                scraped_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                channel_id TEXT PRIMARY KEY,
                channel_title TEXT NOT NULL,
                channel_url TEXT NOT NULL,
                subscriber_count INTEGER,
                video_count INTEGER,
                description TEXT,
                thumbnail TEXT,
                scraped_at TEXT NOT NULL
            )
        ''')

        # Clean up any existing data issues
        try:
            # Fix any NULL published_at values in existing data
            current_time = datetime.now().isoformat()
            cursor.execute('''
                UPDATE videos
                SET published_at = ?
                WHERE published_at IS NULL OR published_at = ''
            ''', (current_time,))

            rows_updated = cursor.rowcount
            if rows_updated > 0:
                print(f"    Fixed {rows_updated} videos with missing published_at dates")

        except sqlite3.Error as e:
            print(f"    Warning: Could not fix existing data: {e}")

        conn.commit()
        conn.close()

    def scrape_channel(self, channel_url: str, max_videos: int = 50, delay: float = 1.0) -> bool:
        """Scrape a YouTube channel using yt-dlp."""
        print(f"Scraping channel: {channel_url}")

        # Use /videos URL directly as it almost always has the most content
        videos_url = channel_url + '/videos' if not channel_url.endswith('/videos') else channel_url

        # yt-dlp options
        ydl_opts = {
            'extract_flat': False,
            'writeinfojson': False,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'playlistend': max_videos,  # Limit number of videos
            'ignoreerrors': True,  # Continue on errors
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First get channel info
                print("  Getting channel info...")
                channel_info = ydl.extract_info(channel_url, download=False, process=False)

                if not channel_info:
                    print("  ❌ Could not extract channel info")
                    return False

                # Extract channel details
                channel_data = self._extract_channel_data(channel_info)
                if channel_data:
                    self.save_channel_to_db(channel_data)

                # Get videos from the /videos page
                print(f"  Getting up to {max_videos} videos from /videos page...")

                # Extract videos with full info
                ydl_opts['extract_flat'] = False
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_full:
                    info = ydl_full.extract_info(videos_url, download=False)

                    if 'entries' in info:
                        videos = []
                        for entry in info['entries']:
                            if entry is None:
                                continue

                            video_data = self._extract_video_data(entry)
                            if video_data:
                                videos.append(video_data)

                            # Add delay to be respectful
                            time.sleep(delay)

                        # Sort by view count and take top videos
                        videos.sort(key=lambda x: x.get('view_count', 0), reverse=True)
                        videos = videos[:max_videos]

                        print(f"  💾 Saving {len(videos)} videos to database...")
                        self.save_videos_to_db(videos)

                        channel_name = channel_data.get('channel_title', 'Unknown') if channel_data else 'Unknown'
                        print(f"  ✅ Successfully scraped {len(videos)} videos from {channel_name}")
                        return True
                    else:
                        print("  ❌ No videos found in /videos page")
                        return False

        except Exception as e:
            print(f"  ❌ Error scraping channel: {e}")
            return False

    def _extract_channel_data(self, info: Dict) -> Optional[Dict]:
        """Extract channel data from yt-dlp info."""
        try:
            return {
                'channel_id': info.get('channel_id') or info.get('uploader_id') or 'unknown',
                'channel_title': info.get('channel') or info.get('uploader') or 'Unknown',
                'channel_url': info.get('channel_url') or info.get('webpage_url') or '',
                'subscriber_count': info.get('channel_follower_count') or 0,
                'description': info.get('description') or '',
                'thumbnail': self._get_best_thumbnail(info.get('thumbnails', [])),
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"    Error extracting channel data: {e}")
            return None

    def _extract_video_data(self, info: Dict) -> Optional[Dict]:
        """Extract video data from yt-dlp info."""
        try:
            # Parse upload date
            upload_date = info.get('upload_date')
            if upload_date:
                try:
                    # Convert YYYYMMDD to ISO format
                    upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}T00:00:00Z"
                except:
                    # If date parsing fails, use current date
                    upload_date = datetime.now().isoformat()
            else:
                # If no upload date, use current date as fallback
                upload_date = datetime.now().isoformat()

            # Ensure we have a video ID
            video_id = info.get('id')
            if not video_id:
                print(f"    Skipping video without ID")
                return None

            return {
                'video_id': video_id,
                'title': info.get('title', 'Unknown'),
                'description': info.get('description') or '',
                'channel_id': info.get('channel_id') or info.get('uploader_id') or 'unknown',
                'channel_title': info.get('channel') or info.get('uploader') or 'Unknown',
                'channel_url': info.get('channel_url') or '',
                'channel_subscriber_count': info.get('channel_follower_count') or 0,
                'published_at': upload_date,  # Now guaranteed to have a value
                'duration': info.get('duration') or 0,
                'view_count': info.get('view_count') or 0,
                'like_count': info.get('like_count') or 0,
                'comment_count': info.get('comment_count') or 0,
                'thumbnail': self._get_best_thumbnail(info.get('thumbnails', [])),
                'tags': json.dumps(info.get('tags', [])),
                'categories': json.dumps(info.get('categories', [])),
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"    Error extracting video data: {e}")
            return None

    def _get_best_thumbnail(self, thumbnails: List[Dict]) -> str:
        """Get the best quality thumbnail URL."""
        if not thumbnails:
            return ''

        # Sort by quality (prefer higher resolution)
        sorted_thumbs = sorted(thumbnails, key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
        return sorted_thumbs[0].get('url', '')

    def save_channel_to_db(self, channel_data: Dict):
        """Save channel information to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO channels
            (channel_id, channel_title, channel_url, subscriber_count,
             description, thumbnail, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            channel_data['channel_id'],
            channel_data['channel_title'],
            channel_data['channel_url'],
            channel_data['subscriber_count'],
            channel_data['description'],
            channel_data['thumbnail'],
            channel_data['scraped_at']
        ))

        conn.commit()
        conn.close()

    def save_videos_to_db(self, videos: List[Dict]):
        """Save video information to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved_count = 0
        skipped_count = 0

        for video in videos:
            # Skip videos without required fields
            if not video.get('video_id') or not video.get('published_at'):
                skipped_count += 1
                continue

            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO videos
                    (video_id, title, description, channel_id, channel_title, channel_url,
                     channel_subscriber_count, published_at, duration, view_count, like_count,
                     comment_count, thumbnail, tags, categories, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video['video_id'],
                    video['title'],
                    video['description'],
                    video['channel_id'],
                    video['channel_title'],
                    video['channel_url'],
                    video['channel_subscriber_count'],
                    video['published_at'],
                    video['duration'],
                    video['view_count'],
                    video['like_count'],
                    video['comment_count'],
                    video['thumbnail'],
                    video['tags'],
                    video['categories'],
                    video['scraped_at']
                ))
                saved_count += 1

            except sqlite3.Error as e:
                print(f"    Database error for video {video.get('video_id', 'unknown')}: {e}")
                skipped_count += 1
                continue

        conn.commit()
        conn.close()

        if skipped_count > 0:
            print(f"    ⚠️  Saved {saved_count} videos, skipped {skipped_count} videos with missing data")

    def scrape_multiple_channels(self, channels: List[str], max_videos_per_channel: int = 50, delay: float = 2.0):
        """Scrape multiple channels."""
        print(f"Starting to scrape {len(channels)} channels...")
        print("=" * 60)

        success_count = 0
        total_videos = 0

        for i, channel_url in enumerate(channels, 1):
            print(f"\n[{i}/{len(channels)}] Processing channel...")

            try:
                success = self.scrape_channel(channel_url, max_videos_per_channel, delay)
                if success:
                    success_count += 1

                    # Count videos for this channel
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM videos WHERE channel_url = ?', (channel_url,))
                    channel_video_count = cursor.fetchone()[0]
                    total_videos += channel_video_count
                    conn.close()

                # Add delay between channels to be respectful
                if i < len(channels):
                    print(f"  ⏰ Waiting {delay * 2}s before next channel...")
                    time.sleep(delay * 2)

            except KeyboardInterrupt:
                print("\n⚠️  Interrupted by user")
                break
            except Exception as e:
                print(f"  ❌ Unexpected error: {e}")

        print("\n" + "=" * 60)
        print(f"📊 Scraping completed!")
        print(f"   ✅ Successful channels: {success_count}/{len(channels)}")
        print(f"   📹 Total videos scraped: {total_videos}")
        print(f"   💾 Database: {self.db_path}")

    def export_to_json(self, output_file: str = 'scraped_data.json'):
        """Export all data to JSON."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all data
        cursor.execute('SELECT * FROM channels ORDER BY subscriber_count DESC')
        channels = [dict(row) for row in cursor.fetchall()]

        cursor.execute('SELECT * FROM videos ORDER BY view_count DESC')
        videos = [dict(row) for row in cursor.fetchall()]

        # Parse JSON fields back to objects
        for video in videos:
            try:
                video['tags'] = json.loads(video['tags']) if video['tags'] else []
                video['categories'] = json.loads(video['categories']) if video['categories'] else []
            except:
                video['tags'] = []
                video['categories'] = []

        data = {
            'channels': channels,
            'videos': videos,
            'total_channels': len(channels),
            'total_videos': len(videos),
            'exported_at': datetime.now().isoformat()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        conn.close()
        print(f"📄 Data exported to: {output_file}")

    def get_stats(self):
        """Print database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM channels')
        channel_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM videos')
        video_count = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(view_count) FROM videos')
        total_views = cursor.fetchone()[0] or 0

        cursor.execute('SELECT channel_title, COUNT(*) as video_count FROM videos GROUP BY channel_id ORDER BY video_count DESC LIMIT 5')
        top_channels = cursor.fetchall()

        cursor.execute('SELECT title, view_count, channel_title FROM videos ORDER BY view_count DESC LIMIT 5')
        top_videos = cursor.fetchall()

        print(f"\n📊 Database Statistics:")
        print(f"   📺 Channels: {channel_count:,}")
        print(f"   📹 Videos: {video_count:,}")
        print(f"   👀 Total views: {total_views:,}")

        print(f"\n🏆 Top 5 Channels by Video Count:")
        for i, (channel, count) in enumerate(top_channels, 1):
            print(f"   {i}. {channel} ({count} videos)")

        print(f"\n🔥 Top 5 Most Viewed Videos:")
        for i, (title, views, channel) in enumerate(top_videos, 1):
            short_title = title[:50] + "..." if len(title) > 50 else title
            print(f"   {i}. {short_title} ({views:,} views) - {channel}")

        conn.close()


# List of 100 popular YouTube channels (you can modify this list)
DEFAULT_CHANNELS = [
    # Tech/Engineering
    "https://www.youtube.com/@veritasium",
    "https://www.youtube.com/@RealEngineering",
    "https://www.youtube.com/@Kurzgesagt",
    "https://www.youtube.com/@TED",
    "https://www.youtube.com/@TEDEd",
    "https://www.youtube.com/@SmarterEveryDay",
    "https://www.youtube.com/@3blue1brown",
    "https://www.youtube.com/@numberphile",
    "https://www.youtube.com/@Computerphile",
    "https://www.youtube.com/@MKBHD",
    "https://www.youtube.com/@UnboxTherapy",
    "https://www.youtube.com/@TechLinked",
    "https://www.youtube.com/@LinusTechTips",

    # Science/Education
    "https://www.youtube.com/@AsapSCIENCE",
    "https://www.youtube.com/@CrashCourse",
    "https://www.youtube.com/@Vsauce",
    "https://www.youtube.com/@minutephysics",
    "https://www.youtube.com/@SteveMould",
    "https://www.youtube.com/@NileRed",
    "https://www.youtube.com/@CGPGrey",
    "https://www.youtube.com/@oversimplified",
    "https://www.youtube.com/@ProfessorDaveExplains",

    # Documentary/Nature
    "https://www.youtube.com/@BBCEarth",
    "https://www.youtube.com/@NatGeo",
    "https://www.youtube.com/@Discovery",
    "https://www.youtube.com/@AnimalPlanet",
    "https://www.youtube.com/@PBS",
    "https://www.youtube.com/@NatGeoWild",

    # Space
    "https://www.youtube.com/@SpaceX",
    "https://www.youtube.com/@NASA",
    "https://www.youtube.com/@EverydayAstronaut",
    "https://www.youtube.com/@IsaacArthur",

    # Gaming
    "https://www.youtube.com/@PewDiePie",
    "https://www.youtube.com/@MrBeast",
    "https://www.youtube.com/@Dude Perfect",
    "https://www.youtube.com/@GameTheory",
    "https://www.youtube.com/@jackspeticeye",

    # Programming
    "https://www.youtube.com/@freecodecamp",
    "https://www.youtube.com/@programmingwithmosh",
    "https://www.youtube.com/@codewitharry",
    "https://www.youtube.com/@NetNinja",
    "https://www.youtube.com/@DerekBanas",

    # Add more channels here...
    # You can extend this list to 100 channels
]


def main():
    """Main function to run the scraper."""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape YouTube channels using yt-dlp')
    parser.add_argument('--channels-file', help='Text file with channel URLs (one per line)')
    parser.add_argument('--max-videos', type=int, default=50, help='Max videos per channel (default: 50)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (default: 1.0s)')
    parser.add_argument('--export', help='Export to JSON file')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--single-channel', help='Scrape a single channel URL')

    args = parser.parse_args()

    scraper = YouTubeDLPScraper()

    if args.stats:
        scraper.get_stats()
        return

    if args.single_channel:
        # Scrape single channel
        success = scraper.scrape_channel(args.single_channel, args.max_videos, args.delay)
        if success and args.export:
            scraper.export_to_json(args.export)
        return

    # Load channel list
    channels = DEFAULT_CHANNELS

    if args.channels_file:
        try:
            with open(args.channels_file, 'r') as f:
                channels = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            print(f"Loaded {len(channels)} channels from {args.channels_file}")
        except FileNotFoundError:
            print(f"Error: File {args.channels_file} not found")
            return

    # Scrape all channels
    scraper.scrape_multiple_channels(channels, args.max_videos, args.delay)

    # Show stats
    scraper.get_stats()

    # Export if requested
    if args.export:
        scraper.export_to_json(args.export)


if __name__ == '__main__':
    main()
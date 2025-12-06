#!/usr/bin/env python3
"""
Script to scrape part 2 database with additional YouTubers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yt_dlp_scraper import YouTubeDLPScraper

def main():
    # Initialize scraper with part 2 database
    scraper = YouTubeDLPScraper(db_path='youtube_videos_part2.db')

    # Load channels from part 2 file
    channels_file = 'channels_list_part2.txt'

    print(f"Starting scraper for part 2 database: youtube_videos_part2.db")
    print(f"Using channels file: {channels_file}")

    try:
        # Load channels from file
        with open(channels_file, 'r') as f:
            channels = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        print(f"Loaded {len(channels)} channels from {channels_file}")

        # Scrape with the part 2 channels
        scraper.scrape_multiple_channels(
            channels=channels,
            max_videos_per_channel=50,
            delay=2.0
        )

        print("\n=== Part 2 Scraping Complete ===")
        scraper.get_stats()

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    main()
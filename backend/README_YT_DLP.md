# YouTube Scraper using yt-dlp

Simple and reliable YouTube channel scraper that doesn't require API keys!

## Features

✅ **No API Keys Required** - Uses yt-dlp instead of YouTube API
✅ **Scrapes Top 50 Popular Videos** from each channel (sorted by views)
✅ **Handles 100+ Channels** easily
✅ **SQLite Database** for data storage
✅ **JSON Export** capability
✅ **Respectful Rate Limiting** with delays
✅ **Resume Support** - can continue from where it left off

## Quick Setup

```bash
# 1. Install yt-dlp
pip install yt-dlp

# 2. Install in your venv
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### 1. Scrape from Channel List File

Edit `channels_list.txt` to add your 100 YouTubers, then run:

```bash
python yt_dlp_scraper.py --channels-file channels_list.txt --max-videos 50
```

### 2. Scrape Single Channel

```bash
python yt_dlp_scraper.py --single-channel "https://www.youtube.com/@veritasium" --max-videos 25
```

### 3. View Statistics

```bash
python yt_dlp_scraper.py --stats
```

### 4. Export to JSON

```bash
python yt_dlp_scraper.py --channels-file channels_list.txt --export scraped_data.json
```

## Channel List Format

Edit `channels_list.txt`:

```txt
# Tech Channels
https://www.youtube.com/@veritasium
https://www.youtube.com/@RealEngineering
https://www.youtube.com/@Kurzgesagt

# Science Channels
https://www.youtube.com/@AsapSCIENCE
https://www.youtube.com/@SciShow

# Add your 100 channels here...
```

## Database Schema

**Videos Table:**
- video_id, title, description
- channel_id, channel_title, channel_url
- view_count, like_count, comment_count
- duration, published_at, thumbnail
- tags, categories (JSON)

**Channels Table:**
- channel_id, channel_title, channel_url
- subscriber_count, description, thumbnail

## Example Output

```
Starting to scrape 5 channels...
============================================================

[1/5] Processing channel...
Scraping channel: https://www.youtube.com/@veritasium
  Getting channel info...
  Getting up to 50 videos...
  💾 Saving 50 videos to database...
  ✅ Successfully scraped 50 videos from Veritasium

[2/5] Processing channel...
...

============================================================
📊 Scraping completed!
   ✅ Successful channels: 5/5
   📹 Total videos scraped: 250
   💾 Database: youtube_videos.db

📊 Database Statistics:
   📺 Channels: 5
   📹 Videos: 250
   👀 Total views: 1,234,567,890

🏆 Top 5 Most Viewed Videos:
   1. The Most Dangerous Stuff in the Universe... (15M views) - Veritasium
   2. How Engineers Design Skyscrapers... (12M views) - Real Engineering
   ...
```

## Tips

### Adding 100 Channels

1. **Find Channel URLs**: Go to any YouTube channel and copy the URL
2. **Multiple Formats Supported**:
   - `https://www.youtube.com/@channelname`
   - `https://www.youtube.com/c/channelname`
   - `https://www.youtube.com/channel/UC...`

3. **Popular Categories**:
   - **Tech**: Veritasium, Real Engineering, MKBHD
   - **Science**: Kurzgesagt, SciShow, AsapSCIENCE
   - **Programming**: freeCodeCamp, Fireship
   - **DIY**: Colin Furze, StuffMadeHere
   - **Gaming**: PewDiePie, MrBeast
   - **Education**: Khan Academy, TED-Ed

### Performance Tips

```bash
# Faster scraping (reduce delay)
python yt_dlp_scraper.py --channels-file channels_list.txt --delay 0.5

# More videos per channel
python yt_dlp_scraper.py --channels-file channels_list.txt --max-videos 100

# Background scraping
nohup python yt_dlp_scraper.py --channels-file channels_list.txt &
```

## Integration with WhyExplore

After scraping, integrate with your app:

```python
# In your Flask app
import sqlite3

def load_videos_from_scraper():
    conn = sqlite3.connect('youtube_videos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM videos
        ORDER BY view_count DESC
        LIMIT 1000
    ''')

    videos = []
    for row in cursor.fetchall():
        video = {
            'videoId': row['video_id'],
            'title': row['title'],
            'channelId': row['channel_id'],
            'channelTitle': row['channel_title'],
            'watchedAt': row['published_at'],
            'duration': row['duration'],
            'category': 'scraped',
            'tags': json.loads(row['tags'] or '[]'),
            'thumbnail': row['thumbnail']
        }
        videos.append(video)

    conn.close()
    return videos
```

## Advantages over API Scraping

✅ **No API Limits** - YouTube API has daily quotas
✅ **No API Keys** - No need to register with Google
✅ **More Data** - Gets data that API doesn't provide
✅ **More Reliable** - yt-dlp is actively maintained
✅ **Handles Private/Unlisted** videos better

## Files Created

- `youtube_videos.db` - SQLite database with all data
- `scraped_data.json` - Exported JSON data (if using --export)
- `channels_list.txt` - Your list of channels to scrape

Perfect for building a comprehensive YouTube recommendation system! 🚀
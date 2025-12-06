# YouTube Channel Video Scraper

This Python script scrapes the top 50 most popular videos from any YouTube channel and stores them in a SQLite database.

## Features

- ✅ Scrapes top videos by view count from any YouTube channel
- ✅ Stores data in SQLite database with proper schema
- ✅ Supports various YouTube channel URL formats
- ✅ Exports data to JSON format
- ✅ Handles API rate limits and pagination
- ✅ Gets detailed video metadata (views, likes, duration, thumbnails, etc.)
- ✅ Stores channel information and statistics

## Setup

### 1. Get YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **YouTube Data API v3**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy your API key

### 2. Install Dependencies

```bash
cd backend
source venv/bin/activate  # or activate your virtual environment
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Scrape by channel ID
python youtube_scraper.py --api-key YOUR_API_KEY --channel-id UC_x5XG1OV2P6uZZ5FSM9Ttw

# Scrape by channel URL
python youtube_scraper.py --api-key YOUR_API_KEY --channel-url "https://www.youtube.com/@RealEngineering"

# Custom number of videos (default is 50)
python youtube_scraper.py --api-key YOUR_API_KEY --channel-id UC_x5XG1OV2P6uZZ5FSM9Ttw --max-videos 100
```

### Export to JSON

```bash
# Scrape and export to JSON
python youtube_scraper.py --api-key YOUR_API_KEY --channel-id UC_x5XG1OV2P6uZZ5FSM9Ttw --export-json channel_data.json
```

### Supported YouTube URL Formats

The scraper supports these YouTube URL formats:

- `https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw`
- `https://www.youtube.com/c/RealEngineering`
- `https://www.youtube.com/user/RealEngineering`
- `https://www.youtube.com/@RealEngineering`

## Database Schema

### Channels Table

```sql
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    channel_title TEXT NOT NULL,
    channel_description TEXT,
    subscriber_count INTEGER,
    video_count INTEGER,
    view_count INTEGER,
    thumbnail_default TEXT,
    thumbnail_medium TEXT,
    thumbnail_high TEXT,
    created_at TEXT,
    scraped_at TEXT NOT NULL
);
```

### Videos Table

```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    channel_id TEXT NOT NULL,
    channel_title TEXT NOT NULL,
    channel_avatar TEXT,
    published_at TEXT NOT NULL,
    duration INTEGER,  -- in seconds
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    thumbnail_default TEXT,
    thumbnail_medium TEXT,
    thumbnail_high TEXT,
    thumbnail_maxres TEXT,
    tags TEXT,  -- JSON string
    category_id TEXT,
    scraped_at TEXT NOT NULL
);
```

## Examples

### Scrape Popular YouTube Channels

```bash
# Real Engineering
python youtube_scraper.py --api-key YOUR_API_KEY --channel-url "https://www.youtube.com/@RealEngineering"

# Veritasium
python youtube_scraper.py --api-key YOUR_API_KEY --channel-url "https://www.youtube.com/@veritasium"

# Kurzgesagt
python youtube_scraper.py --api-key YOUR_API_KEY --channel-url "https://www.youtube.com/@kurzgesagt"

# BBC Earth
python youtube_scraper.py --api-key YOUR_API_KEY --channel-url "https://www.youtube.com/@BBCEarth"

# MrBeast
python youtube_scraper.py --api-key YOUR_API_KEY --channel-url "https://www.youtube.com/@MrBeast"
```

### Query the Database

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('youtube_videos.db')
cursor = conn.cursor()

# Get top 10 most viewed videos
cursor.execute('''
    SELECT title, view_count, channel_title
    FROM videos
    ORDER BY view_count DESC
    LIMIT 10
''')

for title, views, channel in cursor.fetchall():
    print(f"{views:,} views - {title} ({channel})")

conn.close()
```

## Output

### Console Output Example

```
Starting to scrape channel: https://www.youtube.com/@RealEngineering
Channel ID: UC_x5XG1OV2P6uZZ5FSM9Ttw
Fetching channel information...
Channel: Real Engineering
Subscribers: 3,240,000
Total Videos: 284
Fetching top 50 popular videos...
Found 50 videos
Fetching video details...
Saving videos to database...
Successfully scraped 50 videos from Real Engineering
Data saved to: youtube_videos.db
Data exported to: channel_data.json
```

### JSON Export Structure

```json
{
  "channels": [
    {
      "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
      "channel_title": "Real Engineering",
      "subscriber_count": 3240000,
      "video_count": 284,
      "view_count": 521789432
    }
  ],
  "videos": [
    {
      "video_id": "abc123",
      "title": "How Modern Bridges Are Built",
      "view_count": 5200000,
      "duration": 934,
      "tags": ["engineering", "bridges", "construction"]
    }
  ],
  "total_channels": 1,
  "total_videos": 50
}
```

## API Limits

- YouTube Data API has daily quotas
- Free tier: 10,000 quota units per day
- Each video details request costs ~1-4 units
- Each channel search costs ~100 units
- Monitor your usage in Google Cloud Console

## Error Handling

The scraper handles:
- Invalid channel URLs/IDs
- API rate limits
- Network errors
- Missing video data
- Private/deleted videos

## Integration with WhyExplore

To integrate scraped data with the WhyExplore platform:

1. Run the scraper to populate the database
2. Update `app.py` to read from the SQLite database instead of JSON files
3. Use the real video data for recommendations

```python
# Example integration in app.py
import sqlite3

def load_videos_from_db():
    conn = sqlite3.connect('youtube_videos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM videos ORDER BY view_count DESC')
    videos = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return videos
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your API key is valid and YouTube Data API v3 is enabled
2. **Channel Not Found**: Verify the channel URL or ID is correct
3. **Rate Limit**: Reduce the number of videos or wait before running again
4. **Permission Error**: Make sure you have write permissions in the directory

### Debug Mode

Add debug logging by modifying the script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This tool is for educational and research purposes. Respect YouTube's Terms of Service and API usage policies.
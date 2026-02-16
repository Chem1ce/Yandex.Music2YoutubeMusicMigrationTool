import sqlite3
from .track import Track


class MusicCache:
    """Manages local caching of Yandex Music to YouTube Music ID mappings."""

    def __init__(self, db_path='music_cache.db'):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        """Returns a standard sqlite3 connection."""
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """Initializes the database schema if it doesn't exist."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS track_mapping (
                    yandex_key TEXT PRIMARY KEY,
                    youtube_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def get_youtube_id(self, track: Track):
        """Retrieves a cached YouTube Video ID for a given Track object."""
        key = f"{track.artist} - {track.name}".lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT youtube_id FROM track_mapping WHERE yandex_key = ?', (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_mapping(self, track: Track, youtube_id: str):
        """Caches the mapping between a Yandex track and a YouTube Video ID."""
        key = f"{track.artist} - {track.name}".lower()
        with self._get_connection() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO track_mapping (yandex_key, youtube_id) VALUES (?, ?)',
                (key, youtube_id)
            )
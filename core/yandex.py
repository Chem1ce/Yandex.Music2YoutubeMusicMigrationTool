from yandex_music import Client
from typing import List, Optional, Callable
from .track import Track


class YandexMusicExporter:
    """Handles data extraction from Yandex Music API."""

    def __init__(self, token: str):
        try:
            self.client = Client(token).init()
            print("✅ Yandex Music: Authentication successful")
        except Exception as e:
            raise PermissionError(f"Yandex Token Error: {e}")

    def export_liked_tracks(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Track]:
        """Fetches all liked tracks and converts them to the internal Track format."""
        print("📥 Fetching liked tracks from cloud...")
        likes = self.client.users_likes_tracks()
        if not likes or not likes.tracks:
            return []

        track_ids = [t.track_id for t in likes.tracks]
        full_tracks = []
        batch_size = 1000

        # Fetch full track metadata in chunks
        for i in range(0, len(track_ids), batch_size):
            chunk = track_ids[i:i + batch_size]
            full_tracks.extend(self.client.tracks(chunk))

        result = []
        total = len(full_tracks)
        print(f"⚙️ Processing metadata for {total} tracks...")

        for i, t in enumerate(full_tracks):
            artist = t.artists[0].name if t.artists else "Unknown"
            result.append(Track(
                artist=artist,
                name=t.title,
                duration_ms=t.duration_ms or 0
            ))

            if progress_callback:
                progress_callback(i + 1, total)

        return result
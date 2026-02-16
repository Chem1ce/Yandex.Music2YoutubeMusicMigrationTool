import json
import time
from typing import Optional, Callable, List
from ytmusicapi import YTMusic
from thefuzz import fuzz
from .track import Track
from .db import MusicCache


class YoutubeImporter:
    """Handles track searching and playlist population on YouTube Music."""

    def __init__(self, auth_file: str = 'headers.json'):
        self.cache = MusicCache()
        try:
            with open(auth_file, 'r', encoding='utf-8') as f:
                h = json.load(f)
            # Normalize headers keys for ytmusicapi
            clean_h = {k.replace('_', '-').title(): v for k, v in h.items()}
            self.ytmusic = YTMusic(auth=json.dumps(clean_h))
            print("✅ YouTube Music: Authentication successful")
        except Exception as e:
            print(f"❌ Critical YT authentication error: {e}")
            raise

    def _search_best_match(self, track: Track) -> Optional[str]:
        """Searches for a track on YT Music and returns the most relevant videoId."""
        cached_id = self.cache.get_youtube_id(track)
        if cached_id:
            return cached_id

        query = f"{track.artist} - {track.name}"
        try:
            results = self.ytmusic.search(query, filter="songs", limit=3)
            if not results:
                return None

            best_v_id = None
            highest_score = 0

            for res in results:
                full_res_name = f"{res['artists'][0]['name']} {res['title']}"
                score = fuzz.token_sort_ratio(f"{track.artist} {track.name}", full_res_name)

                # Matching threshold to avoid wrong results
                if score > highest_score and score > 70:
                    highest_score = score
                    best_v_id = res['videoId']

            if best_v_id:
                self.cache.save_mapping(track, best_v_id)
            return best_v_id
        except Exception as e:
            print(f"⚠️ Search error for {query}: {e}")
            return None

    def sync_playlist_smart(self, source_tracks: List[Track], playlist_id: str,
                            progress_callback: Optional[Callable[[int, int], None]] = None):
        """Synchronizes source tracks into a target YouTube playlist with duplicate detection."""
        stats = {'added': 0, 'skipped': 0, 'not_found': 0, 'failed': 0}
        total = len(source_tracks)

        print("🛰️ Analyzing existing YouTube playlist...")
        try:
            playlist_data = self.ytmusic.get_playlist(playlist_id, limit=None)
            existing_video_ids = {item['videoId'] for item in playlist_data['tracks']}
        except Exception:
            existing_video_ids = set()

        to_add_ids = []
        print(f"🔍 Searching for tracks...")
        for i, track in enumerate(source_tracks):
            v_id = self._search_best_match(track)
            if not v_id:
                stats['not_found'] += 1
            elif v_id in existing_video_ids:
                stats['skipped'] += 1
            else:
                to_add_ids.append(v_id)

            if progress_callback:
                progress_callback(i + 1, total)

        if to_add_ids:
            batch_size = 20
            print(f"📥 Processing {len(to_add_ids)} new tracks...")

            for i in range(0, len(to_add_ids), batch_size):
                chunk = to_add_ids[i:i + batch_size]
                try:
                    # Attempt batch insertion
                    res = self.ytmusic.add_playlist_items(playlist_id, chunk)
                    if res and res.get('status') == 'STATUS_SUCCEEDED':
                        stats['added'] += len(chunk)
                    else:
                        raise ValueError("Operation status not confirmed")
                    time.sleep(0.8)

                except Exception:
                    # Fallback to single insertion if batch fails (useful for identifying "broken" track IDs)
                    print(f"⚠️ Batch {i} failed. Switching to individual processing...")
                    for single_id in chunk:
                        try:
                            self.ytmusic.add_playlist_items(playlist_id, [single_id])
                            stats['added'] += 1
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"❌ Track {single_id} rejected by server: {e}")
                            stats['failed'] += 1
        return stats
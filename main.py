import sys
import os
import json
import threading

from core.ui import MusicTransferUI, ConsoleRedirector
from core.yandex import YandexMusicExporter
from core.youtube import YoutubeImporter

CONFIG_FILE = 'settings.json'
YT_HEADERS_FILE = 'headers.json'

class Controller:
    """Main application controller linking logic and UI."""

    def __init__(self):
        self.ui = MusicTransferUI(
            on_save_callback=self.save_settings,
            on_start_callback=self.start_transfer
        )
        self.yt = None

        # Redirect standard output to UI console
        sys.stdout = ConsoleRedirector(self.ui.status_box)

        # Initialize UI state
        self.ui.btn_sync.configure(state="disabled", text="Waiting for Auth...")

        self.load_initial()
        self.ui.mainloop()

    def load_initial(self):
        """Loads existing configuration and initializes YouTube client on startup."""
        if os.path.exists(YT_HEADERS_FILE):
            self.ui.badge_json.configure(text="Headers.JSON: FOUND", text_color="#3B82F6")
            threading.Thread(target=self.init_yt, daemon=True).start()
        else:
            print(f"⚠️ File {YT_HEADERS_FILE} not found.")

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    token = data.get("yandex_token", "")
                    self.ui.entry_yandex.insert(0, token)
            except Exception as e:
                print(f"❌ Configuration error: {e}")

    def save_settings(self):
        """Saves Yandex token and triggers re-initialization."""
        token = self.ui.entry_yandex.get().strip()
        if not token:
            print("❗ Please enter a token")
            return

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"yandex_token": token}, f, indent=4)

        print("💾 Settings saved.")
        threading.Thread(target=self.init_yt, daemon=True).start()

    def init_yt(self):
        """Initializes the YouTube client and updates UI state."""
        try:
            self.yt = YoutubeImporter(auth_file=YT_HEADERS_FILE)
            self.ui.badge_google.configure(text="Google Auth: OK", text_color="#10B981")

            # Fetch user playlists for the dropdown
            pls = self.yt.ytmusic.get_library_playlists(limit=50)
            self.ui.playlists_map = {p['title']: p['playlistId'] for p in pls}
            titles = list(self.ui.playlists_map.keys()) + [self.ui.create_new_option]

            self.ui.unlock_interface(titles)
            print("✅ System ready for transfer.")

        except Exception as e:
            self.ui.badge_google.configure(text="GOOGLE: ERROR", text_color="#EF4444")
            print(f"❌ Authentication failed: {e}")

    def start_transfer(self):
        """Triggers the transfer process in a background thread."""
        self.ui.btn_sync.configure(state="disabled", text="Working...")
        threading.Thread(target=self.run_sync, daemon=True).start()

    def run_sync(self):
        """Core migration logic execution."""
        try:
            choice = self.ui.playlist_combo.get()
            is_new = (choice == self.ui.create_new_option)
            target_id = self.ui.playlists_map.get(choice, "LM")

            with open(CONFIG_FILE, 'r') as f:
                token = json.load(f)["yandex_token"]

            # Phase 1: Collect
            print("\n[1/2] Exporting tracks from Yandex...")
            self.ui.update_progress(0, 100)
            yandex = YandexMusicExporter(token)
            tracks = yandex.export_liked_tracks(progress_callback=self.ui.update_progress)

            if not tracks:
                print("📭 No tracks found in the source.")
                return

            # Reverse to maintain original "last liked" order
            tracks.reverse()

            # Phase 2: Transfer
            print(f"\n[2/2] Importing {len(tracks)} tracks to YouTube...")
            if is_new:
                target_id = self.yt.ytmusic.create_playlist("Synced from Yandex", "Automated Import")

            self.ui.update_progress(0, 100)
            stats = self.yt.sync_playlist_smart(tracks, target_id, progress_callback=self.ui.update_progress)

            print(f"\n✨ Operation completed!")
            print(f"Added: {stats['added']} | Skipped: {stats['skipped']} | Failed: {stats['failed']}")

        except Exception as e:
            print(f"\n💥 Error: {e}")
        finally:
            self.ui.btn_sync.configure(state="normal", text="Start Transfer")
            self.ui.update_progress(100, 100)

if __name__ == "__main__":
    Controller()
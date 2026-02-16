import customtkinter as ctk
import sys

class ConsoleRedirector:
    """Redirects stdout to a GUI textbox with basic color-coded log levels."""

    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        if not text.strip() and text != '\n':
            return

        # Clean control characters and progress bar artifacts
        clean_text = text.replace('\r', '').replace('█', '')
        self.textbox.configure(state="normal")

        # Assign tags based on message content for highlighting
        tag = "info"
        lower_text = text.lower()
        if "error" in lower_text or "❌" in text or "fail" in lower_text:
            tag = "error"
        elif "success" in lower_text or "✅" in text or "done" in lower_text:
            tag = "success"

        self.textbox.insert("end", clean_text, tag)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass

class MusicTransferUI(ctk.CTk):
    def __init__(self, on_save_callback, on_start_callback):
        super().__init__()
        self.on_save = on_save_callback
        self.on_start = on_start_callback
        self.create_new_option = "[ Create New Playlist ]"
        self.playlists_map = {}
        self.is_confirmed = False

        # Window configuration
        self.title("YaMusic 2 YTMusic")
        self.geometry("580x820")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0A0A0A")

        # UI Color Palette
        self.accent_color = "#3B82F6"
        self.confirm_color = "#91b9f6"
        self.bg_secondary = "#111111"
        self.border_color = "#1F1F1F"

        self._setup_ui()

    def _setup_ui(self):
        # Header
        ctk.CTkLabel(self, text="Yandex Music 2 Youtube Music", font=("Inter", 24, "bold"), text_color="#BEBEBE").pack(
            pady=(30, 15))

        # Credentials & Settings Section
        self.card = ctk.CTkFrame(self, fg_color=self.bg_secondary, corner_radius=16, border_width=1,
                                 border_color=self.border_color)
        self.card.pack(pady=5, padx=35, fill="x")

        self.input_container = ctk.CTkFrame(self.card, fg_color="transparent")
        self.input_container.pack(pady=(20, 10), padx=20, fill="x")

        self.entry_yandex = ctk.CTkEntry(
            self.input_container, height=45, placeholder_text="Yandex Music Token",
            fg_color="#080808", border_color="#262626", corner_radius=10, font=("Inter", 12)
        )
        self.entry_yandex.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_paste = ctk.CTkButton(
            self.input_container, text="PASTE", width=70, height=45,
            fg_color="#1A1A1A", hover_color="#262626", corner_radius=10,
            font=("Inter", 12, "bold"), command=self._paste_from_clipboard
        )
        self.btn_paste.pack(side="right")

        # Status Badges
        self.badge_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.badge_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.badge_json = self.create_badge(self.badge_frame, "JSON: IDLE", "#444444")
        self.badge_google = self.create_badge(self.badge_frame, "GOOGLE: IDLE", "#444444")
        self.badge_json.pack(side="left", padx=(0, 8))
        self.badge_google.pack(side="left")

        self.btn_save = ctk.CTkButton(
            self.card, text="Verify Token", height=32, width=120,
            fg_color="#222222", hover_color="#2A2A2A", font=("Inter", 12, "bold"),
            corner_radius=8, command=self.on_save
        )
        self.btn_save.pack(pady=(0, 20), padx=20, anchor="e")

        # Destination Selection
        select_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_frame.pack(pady=15, padx=35, fill="x")
        ctk.CTkLabel(select_frame, text="Destination Playlist", font=("Inter", 24, "bold"), text_color="#BEBEBE").pack(
            anchor="center", padx=5)

        self.playlist_combo = ctk.CTkComboBox(
            select_frame, values=["Authorize to load playlists..."], width=520, height=45,
            fg_color=self.bg_secondary, button_color=self.accent_color,
            border_color=self.border_color, corner_radius=10, font=("Inter", 12, "bold"),
            state="disabled"
        )
        self.playlist_combo.pack(pady=(5, 0), fill="x")

        # Console Output
        self.status_box = ctk.CTkTextbox(
            self, height=220, fg_color="#050505", text_color="#888888",
            font=("JetBrains Mono", 11), border_width=1, border_color="#161616",
            corner_radius=12, state="disabled"
        )
        self.status_box.pack(pady=15, padx=35, fill="both", expand=True)
        self.status_box.tag_config("info", foreground="#888888")
        self.status_box.tag_config("error", foreground="#EF4444")
        self.status_box.tag_config("success", foreground="#10B981")

        # Sync Button & Progress
        self.btn_sync = ctk.CTkButton(
            self, text="Start Transfer", height=55,
            fg_color=self.accent_color, hover_color="#2563EB",
            font=("Inter", 24, "bold"), corner_radius=12,
            state="disabled", command=self._handle_start_click
        )
        self.btn_sync.pack(pady=(5, 10), padx=35, fill="x")

        self.progress_bar = ctk.CTkProgressBar(self, height=4, progress_color=self.accent_color, fg_color="#141414")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=35, pady=(0, 20))

    def create_badge(self, parent, text, color):
        """Helper to create status badges."""
        return ctk.CTkLabel(parent, text=text, font=("Inter", 10, "bold"), text_color=color,
                            fg_color="#0F0F0F", corner_radius=6, width=100, height=24)

    def unlock_interface(self, playlist_titles):
        """Activates UI elements after successful authorization."""
        self.playlist_combo.configure(state="normal", values=playlist_titles)
        self.playlist_combo.set(playlist_titles[0])
        self.btn_sync.configure(state="normal", text="Start Transfer")
        self.btn_save.configure(text="Verified", state="disabled", fg_color="#064E3B")

    def _handle_start_click(self):
        """Handles the two-step confirmation process for the transfer."""
        if not self.is_confirmed:
            self.is_confirmed = True
            self.btn_sync.configure(text="Confirm Start?", fg_color=self.confirm_color)
            self.after(3000, self.reset_confirmation)
        else:
            self.is_confirmed = False
            self.btn_sync.configure(text="INITIALIZING...", state="disabled")
            self.on_start()

    def reset_confirmation(self):
        """Resets the confirmation state if user doesn't click within the timeout."""
        if self.is_confirmed and self.btn_sync.cget("state") != "disabled":
            self.is_confirmed = False
            self.btn_sync.configure(text="Start Transfer", fg_color=self.accent_color)

    def update_progress(self, current, total):
        """Updates the visual progress bar."""
        if total > 0:
            ratio = current / total
            self.progress_bar.set(ratio)
            self.update_idletasks()

    def _paste_from_clipboard(self):
        """Pastes text from system clipboard into the Yandex token entry."""
        try:
            clipboard = self.clipboard_get().strip()
            self.entry_yandex.delete(0, "end")
            self.entry_yandex.insert(0, clipboard)
        except Exception:
            pass
import os
import shutil
import json
import subprocess
import time
import psutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import pygame
import sys
import tempfile

# ---------- Directories ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SETTINGS_FILE = os.path.join(BASE_DIR, "quickpremiere_settings.json")
FIRST_TIME_FILE = os.path.join(BASE_DIR, "first_time.txt")  # Track first-time users

# ---------- Helper Functions ----------
def find_premiere_path():
    for d in (r"C:\Program Files\Adobe", r"C:\Program Files (x86)\Adobe"):
        if os.path.exists(d):
            for folder in os.listdir(d):
                if "Premiere Pro" in folder:
                    path = os.path.join(d, folder, "Adobe Premiere Pro.exe")
                    if os.path.exists(path):
                        return path
    return None

def wait_for_premiere_ready():
    """Waits for Premiere splash to end and main window to stabilize"""
    time.sleep(2)
    splash_found = False
    for _ in range(60):
        found = any("Adobe Premiere Pro" in (p.name() or "") for p in psutil.process_iter(['name']))
        if found:
            splash_found = True
            break
        time.sleep(1)
    if not splash_found:
        return False
    time.sleep(5)
    for _ in range(40):
        try:
            procs = [p for p in psutil.process_iter(['name', 'status']) if "Adobe Premiere Pro" in (p.name() or "")]
            if procs:
                p = procs[0]
                if p.status() == psutil.STATUS_RUNNING:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_first_time_user():
    """Check if the user is running the program for the first time."""
    return not os.path.exists(FIRST_TIME_FILE)

def mark_as_returning_user():
    """Mark the user as a returning user."""
    with open(FIRST_TIME_FILE, 'w') as f:
        f.write('This is not the first time.')

# ---------- Main App ----------
class QuickPremiere(ctk.CTk):
    def __init__(self):
        super().__init__()
        # ---------- Theme ----------
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("quickpremiere")
        self.geometry("640x460")
        self.resizable(False, False)
        self.configure(fg_color="#1f1f1f")

        # ---------- Icon ----------
        icon_path = os.path.join(ASSETS_DIR, "Icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # ---------- Fonts ----------
        self.font_header = ("Arial", 22, "bold")
        self.font_body = ("Arial", 16)
        self.font_sub = ("Arial", 12)

        # ---------- Colors ----------
        self.button_color = "#68659E"
        self.button_hover = "#5B5890"
        self.entry_border_color = "#68659E"
        self.checkbox_color = "#68659E"

        # ---------- Settings ----------
        self.settings = load_settings()
        self.premiere_path = self.settings.get("premiere_path")
        self.project_folder = None
        self.splash_disabled = self.settings.get("disable_splash", False)

        # ---------- Splash Setup ----------
        pygame.mixer.init()

        # Define temp folder specifically for splash sound and other assets
        self.temp_dir = tempfile.mkdtemp()  # Create a temporary folder
        self.splash_sound_path = os.path.join(ASSETS_DIR, "splash.mp3")

        # ---------- Start ----------
        if not self.premiere_path or not os.path.exists(self.premiere_path):
            self.show_premiere_selection()
        else:
            self.show_project_location_selection()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ---------- Splash Play ----------
    def play_splash(self):
        if os.path.exists(self.splash_sound_path) and not self.splash_disabled:
            pygame.mixer.music.load(self.splash_sound_path)
            pygame.mixer.music.play()

    def stop_splash(self):
        """Stop splash sound if it is playing."""
        pygame.mixer.music.stop()

    # ---------- Premiere Path ----------
    def show_premiere_selection(self):
        self.clear_window()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both")
        frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Play splash on first page (only if it's the first time)
        if is_first_time_user():
            self.play_splash()
            mark_as_returning_user()  # Mark as returning after splash plays

        # Header label
        ctk.CTkLabel(frame, text="Select Premiere Installation", font=self.font_header).grid(row=1, column=0, pady=(0, 6))

        auto_path = find_premiere_path()
        if auto_path:
            display_text = auto_path
            if len(display_text) > 70:
                display_text = display_text[:67] + "..."
            # Path label
            path_label = ctk.CTkLabel(frame, text=f"Detected: {display_text}", font=self.font_body, wraplength=580, justify="center")
            path_label.grid(row=2, column=0, pady=(0, 3))

            # Tooltip for full path
            def show_tooltip(event):
                x, y = event.x_root + 10, event.y_root + 10
                self.tooltip = ctk.CTkToplevel()
                self.tooltip.geometry(f"+{x}+{y}")
                self.tooltip.overrideredirect(True)
                ctk.CTkLabel(self.tooltip, text=auto_path, font=self.font_sub).pack(padx=5, pady=3)

            def hide_tooltip(event):
                if hasattr(self, "tooltip"):
                    self.tooltip.destroy()

            path_label.bind("<Enter>", show_tooltip)
            path_label.bind("<Leave>", hide_tooltip)

        # Use This button
        ctk.CTkButton(frame, text="Use This", fg_color=self.button_color, hover_color=self.button_hover, command=lambda: self.save_premiere_path(auto_path)).grid(row=3, column=0, pady=(3, 3))

        # Browse manually button
        ctk.CTkButton(frame, text="Browse Manually", fg_color=self.button_color, hover_color=self.button_hover, command=self.browse_premiere).grid(row=4, column=0, pady=(3, 3))

        # Footer
        ctk.CTkLabel(frame, text="quickpremiere - v1.0.1", font=("Arial", 10, "italic"), text_color="gray").grid(row=5, column=0, pady=(20, 0))

    def browse_premiere(self):
        file_path = filedialog.askopenfilename(
            title="Select Premiere Pro executable", filetypes=[("Premiere Executable", "*.exe")], initialdir=r"C:\Program Files\Adobe"
        )
        if file_path:
            self.save_premiere_path(file_path)

    def save_premiere_path(self, path):
        self.premiere_path = path
        self.settings["premiere_path"] = path
        save_settings(self.settings)
        self.show_project_location_selection()

    # ---------- Project Folder ----------
    def show_project_location_selection(self):
        self.clear_window()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both")
        frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Play splash on returning users (only once)
        if not self.splash_disabled:
            self.play_splash()

        ctk.CTkLabel(frame, text="Choose where your files will go for this project", font=self.font_header, wraplength=580, justify="center").grid(row=1, column=0, pady=(0, 6))

        ctk.CTkButton(frame, text="Select Folder", fg_color=self.button_color, hover_color=self.button_hover, command=self.select_project_folder).grid(row=2, column=0, pady=(3, 3))

        # Footer
        ctk.CTkLabel(frame, text="quickpremiere - v1.0", font=("Arial", 10, "italic"), text_color="gray").grid(row=3, column=0, pady=(20, 0))

    def select_project_folder(self):
        self.project_folder = filedialog.askdirectory(title="Select project folder")
        if self.project_folder:
            self.show_main_screen()

    # ---------- Main Screen ----------
    def show_main_screen(self):
        self.clear_window()
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both")
        frame.grid_columnconfigure(0, weight=1)

        # Banner Image (scaled down 50%)
        banner_path = os.path.join(ASSETS_DIR, "banner.png")
        if os.path.exists(banner_path):
            banner_img = Image.open(banner_path)
            banner_img.thumbnail((250, 75), Image.LANCZOS)
            banner_ctk = ctk.CTkImage(light_image=banner_img, dark_image=banner_img, size=banner_img.size)
            ctk.CTkLabel(frame, image=banner_ctk, text="").grid(row=0, column=0, pady=20)

        # Project Name Input
        ctk.CTkLabel(frame, text="Project Name:", font=self.font_body).grid(row=1, column=0, pady=(10, 2))
        self.project_name_entry = ctk.CTkEntry(frame, width=240, border_color=self.entry_border_color, fg_color="#2A2A2A")
        self.project_name_entry.grid(row=2, column=0, pady=(0, 10))

        # Orientation Options
        self.orientation = ctk.StringVar(value="Horizontal")
        ctk.CTkCheckBox(frame, text="Vertical Video", variable=self.orientation, onvalue="Vertical", offvalue="Horizontal", fg_color=self.checkbox_color, hover_color=self.button_hover).grid(row=3, column=0, pady=10)

        # Resolution Dropdown
        self.resolution_options = {
            "Horizontal": ["1920x1080", "2560x1440", "3840x2160", "1280x720", "1440x1080"],
            "Vertical": ["1080x1920", "1440x2560", "2160x3840", "720x1280", "1080x1440"]
        }

        ctk.CTkLabel(frame, text="Resolution:", font=self.font_body).grid(row=4, column=0)
        self.resolution_dropdown = ctk.CTkOptionMenu(frame, values=self.resolution_options["Horizontal"], fg_color=self.button_color, button_color=self.button_color, button_hover_color=self.button_hover)
        self.resolution_dropdown.grid(row=5, column=0, pady=5)

        self.orientation.trace("w", self.update_resolutions)

        # FPS Dropdown
        ctk.CTkLabel(frame, text="Frame Rate:", font=self.font_body).grid(row=6, column=0)
        self.fps_dropdown = ctk.CTkOptionMenu(frame, values=["30", "60"], fg_color=self.button_color, button_color=self.button_color, button_hover_color=self.button_hover)
        self.fps_dropdown.grid(row=7, column=0, pady=5)

        # Create Project Button
        ctk.CTkButton(frame, text="Create Project", fg_color=self.button_color, hover_color=self.button_hover, command=self.create_project).grid(row=8, column=0, pady=20)

        # Footer
        ctk.CTkLabel(frame, text="quickpremiere - v1.0", font=("Arial", 10, "italic"), text_color="gray").grid(row=9, column=0, pady=5)

    def update_resolutions(self, *args):
        orientation = self.orientation.get()
        self.resolution_dropdown.configure(values=self.resolution_options[orientation])
        self.resolution_dropdown.set(self.resolution_options[orientation][0])

    def create_project(self):
        project_name = self.project_name_entry.get().strip()
        orientation = self.orientation.get()
        resolution = self.resolution_dropdown.get()
        fps = self.fps_dropdown.get()

        if not project_name:
            messagebox.showerror("Error", "Please enter a project name.")
            return

        template_file = os.path.join(TEMPLATES_DIR, f"{resolution}_{fps}.prproj")
        if not os.path.exists(template_file):
            messagebox.showerror("Error", f"Template not found: {template_file}")
            return

        dest_project = os.path.join(self.project_folder, f"{project_name}.prproj")
        os.makedirs(os.path.dirname(dest_project), exist_ok=True)
        shutil.copy(template_file, dest_project)

        # Launch Premiere
        subprocess.Popen([self.premiere_path])
        if wait_for_premiere_ready():
            subprocess.Popen([dest_project], shell=True)
        else:
            messagebox.showwarning("Warning", "Premiere did not stabilize in time. Please open the project manually.")

        self.stop_splash()  # Stop splash sound when done

        self.destroy()

if __name__ == "__main__":
    app = QuickPremiere()
    app.mainloop()

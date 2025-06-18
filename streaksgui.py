# MIT License

# Copyright (c) 2025 Abhishek Mishra (neolateral.in)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
streaksgui.py - Tkinter GUI for the streak.txt format.
A simple GUI to quickly mark daily streaks.

author: Abhishek Mishra
date: 18/06/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
from streakdottxt import Streak, DEFAULT_STREAKS_DIR


class QuickTickDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Streak Quick Tick")
        self.root.geometry("600x500")

        # Directory setup
        self.streaks_dir = DEFAULT_STREAKS_DIR
        self.streaks = []

        self.setup_ui()
        self.load_streaks()

    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.root, text="Today's Streaks", font=("Arial", 18, "bold")
        )
        title_label.pack(pady=15)

        # Date display
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        date_label = tk.Label(self.root, text=today, font=("Arial", 14))
        date_label.pack(pady=5)

        # Main content frame
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollable frame for streaks
        canvas = tk.Canvas(content_frame)
        scrollbar = ttk.Scrollbar(
            content_frame, orient="vertical", command=canvas.yview
        )
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bottom frame
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=15)

        # Buttons frame
        button_frame = tk.Frame(bottom_frame)
        button_frame.pack(side="top", fill="x", pady=(0, 10))

        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_streaks,
            font=("Arial", 12),
        )
        refresh_btn.pack(side="left")

        new_streak_btn = tk.Button(
            button_frame,
            text="➕ New Streak",
            command=self.create_new_streak,
            font=("Arial", 12),
        )
        new_streak_btn.pack(side="left", padx=(10, 0))

        # Summary label
        self.summary_label = tk.Label(bottom_frame, text="", font=("Arial", 14, "bold"))
        self.summary_label.pack()

    def load_streaks(self):
        """Load all streak files from the directory"""
        if not os.path.exists(self.streaks_dir):
            os.makedirs(self.streaks_dir)

        self.streaks = []
        try:
            files = os.listdir(self.streaks_dir)
            streak_files = [
                f for f in files if f.startswith("streak-") and f.endswith(".txt")
            ]

            for streak_file in streak_files:
                try:
                    streak = Streak(os.path.join(self.streaks_dir, streak_file))
                    self.streaks.append(streak)
                except Exception as e:
                    print(f"Error loading {streak_file}: {e}")
        except Exception as e:
            print(f"Error accessing streaks directory: {e}")

        self.display_streaks()

    def display_streaks(self):
        """Display all streaks with tick buttons"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.streaks:
            no_streaks_label = tk.Label(
                self.scrollable_frame,
                text="No streaks found. Click 'New Streak' to create one!",
                font=("Arial", 14),
                fg="gray",
            )
            no_streaks_label.pack(pady=50)
            self.summary_label.config(text="No streaks to display")
            return

        today = datetime.datetime.now().date()
        ticked_count = 0

        for streak in self.streaks:
            # Check if already ticked today
            already_ticked = any(tick.get_date() == today for tick in streak.ticks)
            if already_ticked:
                ticked_count += 1

            # Create frame for each streak
            streak_frame = tk.Frame(
                self.scrollable_frame, relief="solid", borderwidth=1, bg="white"
            )
            streak_frame.pack(fill="x", padx=5, pady=5)

            # Main content frame
            main_frame = tk.Frame(streak_frame, bg="white")
            main_frame.pack(fill="x", padx=15, pady=15)

            # Left side - streak info
            info_frame = tk.Frame(main_frame, bg="white")
            info_frame.pack(side="left", fill="x", expand=True)

            name_label = tk.Label(
                info_frame, text=streak.name, font=("Arial", 16, "bold"), bg="white"
            )
            name_label.pack(anchor="w")

            # Tick type
            type_label = tk.Label(
                info_frame,
                text=f"Type: {streak.tick}",
                font=("Arial", 10),
                fg="gray",
                bg="white",
            )
            type_label.pack(anchor="w")

            # Stats
            stats = streak.stats
            stats_text = f"Current: {stats['current_streak']} | Longest: {stats['longest_streak']} | Success: {stats['tick_average']*100:.0f}%"
            stats_label = tk.Label(
                info_frame,
                text=stats_text,
                font=("Arial", 11),
                fg="darkblue",
                bg="white",
            )
            stats_label.pack(anchor="w", pady=(5, 0))

            # Right side - tick button
            button_frame = tk.Frame(main_frame, bg="white")
            button_frame.pack(side="right", padx=15)

            if already_ticked:
                tick_btn = tk.Button(
                    button_frame,
                    text="✓ Done Today",
                    bg="#4CAF50",
                    fg="white",
                    state="disabled",
                    width=12,
                    height=2,
                    font=("Arial", 12, "bold"),
                )
            else:
                tick_btn = tk.Button(
                    button_frame,
                    text="Mark Done",
                    bg="#2196F3",
                    fg="white",
                    width=12,
                    height=2,
                    font=("Arial", 12, "bold"),
                    command=lambda s=streak: self.tick_streak(s),
                )

            tick_btn.pack()

        # Update summary
        total_streaks = len(self.streaks)
        completion_rate = (
            (ticked_count / total_streaks * 100) if total_streaks > 0 else 0
        )
        self.summary_label.config(
            text=f"Today's Progress: {ticked_count}/{total_streaks} ({completion_rate:.0f}%)"
        )

    def tick_streak(self, streak):
        """Mark a streak as ticked for today"""
        try:
            streak.mark_today()
            self.display_streaks()  # Refresh the display
            messagebox.showinfo("Success", f"✓ Marked '{streak.name}' for today!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to tick '{streak.name}': {str(e)}")

    def refresh_streaks(self):
        """Reload streaks from disk"""
        self.load_streaks()

    def create_new_streak(self):
        """Open dialog to create a new streak"""
        dialog = NewStreakDialog(self.root, self.streaks_dir)
        if dialog.result:
            self.refresh_streaks()

    def run(self):
        self.root.mainloop()


class NewStreakDialog:
    def __init__(self, parent, streaks_dir):
        self.parent = parent
        self.streaks_dir = streaks_dir
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Streak")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")

        self.setup_dialog()

    def setup_dialog(self):
        # Title
        title_label = tk.Label(
            self.dialog, text="Create New Streak", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=20)

        # Name input
        name_frame = tk.Frame(self.dialog)
        name_frame.pack(pady=10, padx=30, fill="x")

        tk.Label(name_frame, text="Streak Name:", font=("Arial", 12)).pack(anchor="w")
        self.name_entry = tk.Entry(name_frame, font=("Arial", 12))
        self.name_entry.pack(fill="x", pady=(5, 0))
        self.name_entry.focus()

        # Tick type selection
        tick_frame = tk.Frame(self.dialog)
        tick_frame.pack(pady=10, padx=30, fill="x")

        tk.Label(tick_frame, text="Tick Type:", font=("Arial", 12)).pack(anchor="w")
        self.tick_var = tk.StringVar(value="Daily")
        tick_combo = ttk.Combobox(
            tick_frame,
            textvariable=self.tick_var,
            values=["Daily", "Weekly", "Monthly"],
            state="readonly",
            font=("Arial", 12),
        )
        tick_combo.pack(fill="x", pady=(5, 0))

        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=30)

        create_btn = tk.Button(
            button_frame,
            text="Create Streak",
            command=self.create_streak,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=12,
        )
        create_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=("Arial", 12),
            width=12,
        )
        cancel_btn.pack(side="left", padx=5)

        # Bind Enter key to create
        self.dialog.bind("<Return>", lambda e: self.create_streak())

    def create_streak(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a streak name")
            return

        tick_type = self.tick_var.get()

        try:
            # Create filename (similar to CLI logic)
            filename = f"streak-{name.lower().replace(' ', '-')}.txt"
            filepath = os.path.join(self.streaks_dir, filename)

            # Check if file already exists
            if os.path.exists(filepath):
                messagebox.showerror(
                    "Error", f"A streak with name '{name}' already exists"
                )
                return

            # Create the streak file with YAML frontmatter
            with open(filepath, "w") as f:
                f.write("---\n")
                f.write(f"name: {name}\n")
                f.write(f"tick: {tick_type}\n")
                f.write("---\n")

            self.result = True
            messagebox.showinfo("Success", f"Created new streak: '{name}'")
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create streak: {str(e)}")


if __name__ == "__main__":
    app = QuickTickDashboard()
    app.run()

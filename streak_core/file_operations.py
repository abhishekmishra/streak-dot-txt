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
File operations for the streak.txt format.
Handles loading and saving of streak files.
"""

import os
import sys
from .models import Streak, DailyTick


class StreakFileManager:
    """
    Handles all file I/O operations for streak files.
    """

    @staticmethod
    def load_from_file(filepath):
        """
        Load a streak from a file.
        Returns a Streak object with all data populated.
        """
        streak = Streak()
        streak.streak_file = filepath
        
        # Read metadata and ticks
        StreakFileManager._read_metadata(streak)
        StreakFileManager._read_ticks(streak)
        
        # Calculate derived data
        streak.get_years()
        
        return streak

    @staticmethod
    def save_to_file(streak, filepath=None):
        """
        Save a streak to a file.
        If filepath is not provided, uses the streak's existing file path.
        """
        if filepath is None:
            filepath = getattr(streak, 'streak_file', None)
            if filepath is None:
                raise ValueError("No file path provided and streak has no existing file")        
        with open(filepath, "w") as f:
            # write the metadata
            f.write("---\n")
            # Ensure name and tick are in metadata
            if streak.name:
                streak.metadata["name"] = streak.name
            if streak.tick:
                streak.metadata["tick"] = streak.tick
            
            for key, value in streak.metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("---\n")            # write the ticks
            for tick in streak.ticks:
                f.write(f"{tick.tick_datetime_str}\n")

    @staticmethod
    def _read_metadata(streak):
        """
        Read YAML front matter metadata from the streak file.
        """
        with open(streak.streak_file, "r") as f:
            line = f.readline()
            if line == "---\n":
                while True:
                    line = f.readline()
                    if line != "---\n":
                        if ": " in line:
                            key, value = line.split(": ", 1)
                            key = key.strip()
                            value = value.strip()
                            streak.metadata[key] = value
                    else:
                        break
        
        if "name" in streak.metadata:
            streak.name = streak.metadata["name"]
        if "tick" in streak.metadata:
            streak.tick = streak.metadata["tick"]
            # Set period based on tick type
            if streak.tick == "Daily":
                streak.period = 1
            elif streak.tick == "Weekly":
                streak.period = 7
            else:
                raise ValueError(f"Unsupported tick type: {streak.tick}")    @staticmethod
    def _read_ticks(streak):
        """
        Read the ticks from the file.

        Supports both Daily and Weekly tick types.
        Each line after the metadata is a tick
        Each tick is in the date format ISO8601
        All of the ticks are stored in the ticks list
        """
        with open(streak.streak_file, "r") as f:
            # gobble up the yaml metadata if it exists
            line = f.readline()
            if line == "---\n":
                while True:
                    line = f.readline()
                    if line == "---\n":
                        break
            # read the ticks
            while line:
                line = f.readline()
                if line and line.strip():
                    streak.ticks.append(DailyTick(line.strip()))

    @staticmethod
    def find_streak_file(directory, name):
        """
        Find a streak file by name in the given directory.
        Returns the full path to the file or None if not found.
        """
        if not os.path.exists(directory):
            return None
            
        files = os.listdir(directory)
        matches = [f for f in files if name.lower() in f.lower()]
        
        if len(matches) == 0:
            return None
        elif len(matches) == 1:
            return os.path.join(directory, matches[0])
        else:
            # Multiple matches found
            raise ValueError(f"Multiple streaks found matching '{name}': {matches}")

    @staticmethod
    def get_streak_from_file_or_name(directory, file_path=None, name=None):
        """
        Get a streak either from a specific file path or by searching for a name.
        """
        if file_path:
            return StreakFileManager.load_from_file(file_path)
        elif name:
            found_file = StreakFileManager.find_streak_file(directory, name)
            if found_file is None:
                print("No streaks found")
                sys.exit(1)
            return StreakFileManager.load_from_file(found_file)
        else:
            print("No file or name provided")
            sys.exit(1)

    @staticmethod
    def create_new_streak_file(directory, name, tick_type="Daily"):
        """
        Create a new streak file with the given name and tick type.
        Returns the path to the created file.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        name_in_path = name.replace(" ", "-").lower()
        streak_file = os.path.join(directory, f"streak-{name_in_path}.txt")
        
        if os.path.exists(streak_file):
            raise FileExistsError(f"Streak file already exists: {streak_file}")        
        with open(streak_file, "w") as f:
            f.write(f"---\nname: {name}\ntick: {tick_type}\n---\n")
        
        return streak_file

    @staticmethod
    def list_streak_files(directory):
        """
        List all streak files in the given directory.
        Returns a list of file paths.
        """
        if not os.path.exists(directory):
            return []
            
        files = os.listdir(directory)
        streak_files = [f for f in files if f.startswith("streak-") and f.endswith(".txt")]
        return [os.path.join(directory, f) for f in streak_files]

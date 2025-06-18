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
streakdottxt.py - Reference implementation of the streak.txt format.
A command line tool to manage daily streaks all stored in text files.

author: Abhishek Mishra
date: 05/01/2025
"""
import sys
import os
import datetime
import click
from rich.console import Console
from rich.table import Table
from rich import box

# Import core functionality
from streak_core import (
    DailyTick, 
    Streak, 
    StreakFileManager, 
    StreakStatsCalculator, 
    TerminalDisplay,
    DEFAULT_STREAKS_DIR
)


# Enhanced Streak class that adds file I/O and statistics calculation
class EnhancedStreak(Streak):
    """
    Enhanced Streak class that combines the core Streak model with file operations
    and statistics calculations for backward compatibility.
    """

    def __init__(self, streak_file):
        # Initialize base streak first
        super().__init__()
        self.streak_file = streak_file
        
        # Load from file using the file manager
        loaded_streak = StreakFileManager.load_from_file(streak_file)
        
        # Copy all attributes from loaded streak
        self.name = loaded_streak.name
        self.tick = loaded_streak.tick
        self.metadata = loaded_streak.metadata
        self.ticks = loaded_streak.ticks
        self.period = loaded_streak.period
        self.years = loaded_streak.years
        self.stats = loaded_streak.stats
        
        # Calculate statistics
        StreakStatsCalculator.calculate_stats(self)

    def mark_today(self):
        """
        Mark today or this week as ticked, but only if it is not already ticked
        """
        result = super().mark_today()
        if result:
            self.write_streak()
            # Recalculate stats after adding tick
            StreakStatsCalculator.calculate_stats(self)
        return result

    def write_streak(self):
        """
        Write the streak to the file
        """
        StreakFileManager.save_to_file(self, self.streak_file)

    def calculate_stats(self):
        """
        Calculate the stats for the streak
        """
        StreakStatsCalculator.calculate_stats(self)

# Backward compatibility - keep the original Streak name
Streak = EnhancedStreak


# TerminalDisplay is now imported from streak_core


@click.group(
    help="The streak command line tool helps you keep track of your daily streaks."
)
@click.option("--dir", default=DEFAULT_STREAKS_DIR, help="Directory to store streaks")
@click.pass_context
def streakdottxt(ctx, dir):
    ctx.ensure_object(dict)
    ctx.obj["dir"] = dir


@streakdottxt.command(help="View the streak")
@click.option("-f", "--file", help="Streak file to view")
@click.option("-n", "--name", help="Name of the streak (fuzzy matched)")
@click.pass_context
def view(ctx, file, name):
    dir = ctx.obj["dir"]
    streak = get_streak_from_file_or_name(dir, file, name)
    display = TerminalDisplay(streak)
    display.display_all()


def mark_streak(dir, file, name):
    streak = get_streak_from_file_or_name(dir, file, name)
    # print the streak name
    print("Streak:", streak.name)
    streak.mark_today()


@streakdottxt.command(help="Mark today's tick")
@click.option("-f", "--file", help="Streak file to mark")
@click.option("-n", "--name", help="Name of the streak (fuzzy matched)")
@click.pass_context
def mark(ctx, file, name):
    dir = ctx.obj["dir"]
    mark_streak(dir, file, name)


@streakdottxt.command(help="Tick today's tick (same as mark)")
@click.option("-f", "--file", help="Streak file to tick")
@click.option("-n", "--name", help="Name of the streak (fuzzy matched)")
@click.pass_context
def tick(ctx, file, name):
    dir = ctx.obj["dir"]
    mark_streak(dir, file, name)


@streakdottxt.command(help="Create a new streak")
@click.option("-n", "--name", required=True, help="Name of the new streak")
@click.pass_context
def new(ctx, name):
    dir = ctx.obj["dir"]
    try:
        streak_file = StreakFileManager.create_new_streak_file(dir, name)
        print(f"Streak '{name}' created at {streak_file}")
    except FileExistsError:
        print("Streak already exists")


@streakdottxt.command(help="List all the streaks in the directory")
@click.pass_context
def list(ctx):
    dir = ctx.obj["dir"]
    streak_files = StreakFileManager.list_streak_files(dir)
    if streak_files:
        table = Table(title="Streaks", box=box.SIMPLE)
        table.add_column("Today")
        table.add_column("Name")
        table.add_column("Tick")
        table.add_column("Longest Streak")
        table.add_column("Current Streak")
        table.add_column("Tick Average")

        for streak_file in streak_files:
            streak = Streak(streak_file)
            today = datetime.datetime.now().date()
            today_status = (
                "✓" if any(tick.get_date() == today for tick in streak.ticks) else "✖"
            )
            table.add_row(
                today_status,
                streak.name,
                streak.tick,
                str(streak.stats["longest_streak"]),
                str(streak.stats["current_streak"]),
                f"{streak.stats['tick_average'] * 100:.0f}%",
            )

        console = Console()
        console.print(table)
    else:
        print("No streaks found")


def get_streak_from_file_or_name(dir, file, name):
    """
    Get a streak from file or name using the StreakFileManager
    """
    return StreakFileManager.get_streak_from_file_or_name(dir, file, name)


if __name__ == "__main__":
    streakdottxt()

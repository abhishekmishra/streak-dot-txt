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
import dateutil.parser
import datetime
import click
from rich.console import Console
from rich.table import Table
from rich import box

# Default directory to store streaks is "streaks" in the home directory
DEFAULT_STREAKS_DIR = os.path.join(os.path.expanduser("~"), "streaks")


class DailyTick:
    """
    DailyTick class represents a tick for a daily streak.
    It has a tick_datetime_str which is the date in ISO8601 format
    and a tick_datetime which is a datetime object parsed from the tick_datetime_str
    """

    def __init__(self, tick_datetime_str):
        self.tick_datetime_str = tick_datetime_str
        # parse ISO8601 date using dateutil.parser
        self.tick_datetime = dateutil.parser.parse(tick_datetime_str)

    def get_year(self):
        return self.tick_datetime.year

    def get_month(self):
        return self.tick_datetime.month

    def get_day(self):
        return self.tick_datetime.day

    def get_weekday(self):
        return self.tick_datetime.weekday()

    def get_week_in_month(self):
        # get the week in the month
        return (self.tick_datetime.day - 1) // 7 + 1

    def get_week_in_year(self):
        # get the week in the year
        return self.tick_datetime.isocalendar()[1]

    def get_date(self):
        return self.tick_datetime.date()

    def __str__(self):
        return self.tick_datetime


class Streak:
    """
    Streak class represents a streak.

    It has a streak_file which is the file where the streak is stored.
    The metadata (name and tick), the ticks, and the stats are read from the file.

    self.period: represents the period of the tick in number of intervals.
                if the task is done once per day then period is 1
                if the task is done once per week then period is 7
                if the task is done once per month then period is the length of the month
    """

    def __init__(self, streak_file):
        self.streak_file = streak_file
        self.metadata = {}
        self.name = None
        self.tick = None
        self.period = None

        self.ticks = []
        self.years = []
        self.stats = {
            "total_days": 0,
            "ticked_days": 0,
            "unticked_days": 0,
            "current_streak": 0,
            "longest_streak": 0,
        }

        # read yaml front matter from the file if they exist
        self.read_metadata()

        # read the ticks from the file
        self.read_ticks()

        # read the years from the ticks
        self.get_years()

        # calculate the stats
        self.calculate_stats()

    def read_metadata(self):
        with open(self.streak_file, "r") as f:
            line = f.readline()
            if line == "---\n":
                while True:
                    line = f.readline()
                    if line != "---\n":
                        key, value = line.split(": ")
                        key = key.strip()
                        value = value.strip()
                        self.metadata[key] = value
                    else:
                        break
        if "name" in self.metadata:
            self.name = self.metadata["name"]
        if "tick" in self.metadata:
            self.tick = self.metadata["tick"]

    def read_ticks(self):
        """
        Read the ticks from the file

        Supports both Daily and Weekly tick types.
        Each line after the metadata is a tick
        Each tick is in the date format ISO8601
        All of the ticks are stored in the ticks list
        """
        if self.tick == "Daily":
            self.period = 1
        elif self.tick == "Weekly":
            self.period = 7
        else:
            raise ValueError(f"Unsupported tick type: {self.tick}")

        with open(self.streak_file, "r") as f:
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
                if line:
                    self.ticks.append(DailyTick(line.strip()))

    def get_years(self):
        """
        Get the years that the streak has been active
        """
        for tick in self.ticks:
            year = tick.get_year()
            if year not in self.years:
                self.years.append(year)
        return self.years

    def mark_today(self):
        """
        Mark today or this week as ticked, but only if it is not already ticked
        """
        today = datetime.datetime.now()
        if self.tick == "Daily":
            today_tick = DailyTick(today.isoformat())
            if today_tick.get_date() not in [tick.get_date() for tick in self.ticks]:
                print("Adding today's tick:", today_tick.tick_datetime)
                self.ticks.append(today_tick)
                self.write_streak()
            else:
                print("Today is already ticked")
        elif self.tick == "Weekly":
            start_of_week = today - datetime.timedelta(days=today.weekday())
            week_tick = DailyTick(start_of_week.isoformat())
            if week_tick.get_week_in_year() not in [
                tick.get_week_in_year() for tick in self.ticks
            ]:
                print("Adding this week's tick:", week_tick.tick_datetime)
                self.ticks.append(week_tick)
                self.write_streak()
            else:
                print("This week is already ticked")

    def write_streak(self):
        """
        Write the streak to the file
        """
        with open(self.streak_file, "w") as f:
            # write the metadata
            f.write("---\n")
            for key, value in self.metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("---\n")
            # write the ticks
            for tick in self.ticks:
                f.write(f"{tick.tick_datetime_str}\n")

    def calculate_stats(self):
        """
        Calculate the stats for the streak

        total_days - total days the streak has been active, first tick to current date
        ticked_days - total days or weeks the streak has been ticked
        unticked_days - total days or weeks the streak has not been ticked (total_days - ticked_days)
        current_streak - current streak of ticked days or weeks
        longest_streak - longest streak of ticked days or weeks
        """
        if not self.ticks:
            self.stats["total_days"] = 0
            self.stats["ticked_days"] = 0
            self.stats["unticked_days"] = 0
            self.stats["current_streak"] = 0
            self.stats["longest_streak"] = 0
            self.stats["tick_average"] = 0
            return

        if self.tick == "Daily":
            self.stats["total_days"] = (
                datetime.datetime.now().date() - self.ticks[0].get_date()
            ).days + 1
        elif self.tick == "Weekly":
            self.stats["total_days"] = (
                (datetime.datetime.now().date() - self.ticks[0].get_date()).days // 7
            ) + 1

        self.stats["ticked_days"] = len(self.ticks)
        self.stats["unticked_days"] = (
            self.stats["total_days"] - self.stats["ticked_days"]
        )
        self.stats["current_streak"] = 0
        self.stats["longest_streak"] = 0

        current_streak = 0
        longest_streak = 0
        today = datetime.datetime.now().date()
        tick_dates = {tick.get_date() for tick in self.ticks}
        last_tick_date = None

        for single_date in (
            self.ticks[0].get_date() + datetime.timedelta(n * self.period)
            for n in range(self.stats["total_days"])
        ):
            if single_date in tick_dates:
                if (
                    last_tick_date is None
                    or (single_date - last_tick_date).days == self.period
                ):
                    current_streak += 1
                else:
                    current_streak = 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
                last_tick_date = single_date
            else:
                current_streak = 0

        self.stats["current_streak"] = current_streak
        self.stats["longest_streak"] = longest_streak
        self.stats["tick_average"] = (
            self.stats["ticked_days"] / self.stats["total_days"]
        )


class TerminalDisplay:
    """
    TerminalDisplay class is used to display the streak information on the terminal.
    """

    def __init__(self, streak):
        self.streak = streak
        self.console = Console()

    def display_all(self):
        """
        Display all the information about the streak
        """
        self.display_streak_info()
        print()
        self.display_streak_stats()
        print()
        self.display_streak_calendar()

    def display_streak_info(self):
        """
        Display the streak information
        """
        print("Name [" + self.streak.name + "]")
        print("Tick [" + self.streak.tick + "]")

    def display_streak_stats(self):
        """
        Display the streak stats in a rich table
        """
        table = Table(title="Streak Stats", box=box.SIMPLE)
        table.add_column("Stat")
        table.add_column("Value")

        table.add_row("Total Days", str(self.streak.stats["total_days"]))
        table.add_row("Ticked Days", str(self.streak.stats["ticked_days"]))
        table.add_row("Unticked Days", str(self.streak.stats["unticked_days"]))
        table.add_row("Current Streak", str(self.streak.stats["current_streak"]))
        table.add_row("Longest Streak", str(self.streak.stats["longest_streak"]))
        table.add_row("Tick Average", f"{self.streak.stats['tick_average'] * 100:.0f}%")

        self.console.print(table)

    def display_streak_calendar(self):
        """
        Display the streak calendar till today's date only for the current year.

        The streak is displayed as a calendar on the terminal.

        Every month is displayed in a grid with the days of a month as cells
        and each line is a week.

        Each cell has a day number and a flag X or empty to indicate if the day
        is ticked or not.

        The first line of the month display has the month name,
        the second line has the days of the week, abbreviated to 3 letters.
        and spaced such that they are centered in the cell.
        """
        current_date = datetime.datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        # get the first day of the year
        first_day = datetime.datetime(current_year, 1, 1)
        # get the last day of the streak is today
        last_day = datetime.datetime(current_year, current_month, current_day)

        # draw all the months till the current month
        for month in range(1, current_month + 1):
            # get the first day of the month
            first_day = datetime.datetime(current_year, month, 1)
            # get the last day of the month
            last_day = datetime.datetime(
                current_year, month + 1, 1
            ) - datetime.timedelta(days=1)
            # draw the month
            self.draw_month(first_day, last_day)

    def draw_month(self, first_day, last_day):
        """
        Draw the month from first_day to last_day
        """
        month_name = first_day.strftime("%B")
        year = first_day.year
        first_weekday = first_day.weekday()
        num_days = (last_day - first_day).days + 1

        ticked_days = {
            tick.get_day()
            for tick in self.streak.ticks
            if tick.get_month() == first_day.month and tick.get_year() == first_day.year
        }

        table = Table(title=month_name + " " + str(year), box=box.SIMPLE)

        table.add_column("Sun", justify="center")
        table.add_column("Mon", justify="center")
        table.add_column("Tue", justify="center")
        table.add_column("Wed", justify="center")
        table.add_column("Thu", justify="center")
        table.add_column("Fri", justify="center")
        table.add_column("Sat", justify="center")

        week = [""] * first_weekday
        current_date = datetime.datetime.now().date()
        for day in range(1, num_days + 1):
            day_date = datetime.date(first_day.year, first_day.month, day)
            if day_date > current_date:
                day_display = f"[on dark_gray]{day:2} [-][/]"
            elif day_date == current_date:
                if day in ticked_days:
                    day_display = f"[bold][on green]{day:2} [✓][/][/bold]"
                else:
                    day_display = f"[bold][on blue]{day:2} [ ][/][/bold]"
            else:
                if day in ticked_days:
                    day_display = f"[on green]{day:2} [✓][/]"
                else:
                    day_display = f"[on red]{day:2} [✖][/]"
            week.append(day_display)
            if len(week) == 7:
                table.add_row(*week)
                week = []
        if week:
            table.add_row(*week)

        self.console.print(table)


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
    name_in_path = name.replace(" ", "-").lower()
    streak_file = os.path.join(dir, f"streak-{name_in_path}.txt")
    if os.path.exists(streak_file):
        print("Streak already exists")
    else:
        with open(streak_file, "w") as f:
            f.write(f"---\nname: {name}\ntick: Daily\n---\n")
        print(f"Streak '{name}' created")


@streakdottxt.command(help="List all the streaks in the directory")
@click.pass_context
def list(ctx):
    dir = ctx.obj["dir"]
    files = os.listdir(dir)
    streak_files = [f for f in files if f.startswith("streak-") and f.endswith(".txt")]
    if streak_files:
        table = Table(title="Streaks", box=box.SIMPLE)
        table.add_column("Today")
        table.add_column("Name")
        table.add_column("Tick")
        table.add_column("Longest Streak")
        table.add_column("Current Streak")
        table.add_column("Tick Average")

        for streak_file in streak_files:
            streak = Streak(os.path.join(dir, streak_file))
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
    if file:
        return Streak(file)
    elif name:
        files = os.listdir(dir)
        matches = [f for f in files if name in f]
        if len(matches) == 0:
            print("No streaks found")
            sys.exit(1)
        elif len(matches) > 1:
            print("Multiple streaks found")
            sys.exit(1)
        else:
            return Streak(os.path.join(dir, matches[0]))
    else:
        print("No file provided")
        sys.exit(1)


if __name__ == "__main__":
    streakdottxt()

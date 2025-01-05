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
    def __init__(self, streak_file):
        self.streak_file = streak_file
        self.metadata = {}
        self.name = None
        self.tick = None

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

        Currently only ticks with tick type "Daily" are supported
        Each line after the metadata is a tick
        Each tick is in the date format ISO8601
        All of the ticks are stored in the ticks list
        """
        if self.tick == "Daily":
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
        Mark today as ticked, but only if it is not already ticked
        """
        # print the tick dates
        for tick in self.ticks:
            print(tick.get_date())
        today = datetime.datetime.now()
        today_tick = DailyTick(today.isoformat())
        # check if today is already ticked
        # match only the date part of the tick
        if today_tick.get_date() not in [tick.get_date() for tick in self.ticks]:
            print("Adding today's tick :", today_tick.tick_datetime)
            self.ticks.append(today_tick)
            self.write_streak()
        else:
            print("Today is already ticked")

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
        ticked_days - total days the streak has been ticked
        unticked_days - total days the streak has not been ticked (total_days - ticked_days)
        current_streak - current streak of ticked days
        longest_streak - longest streak of ticked days
        """
        if not self.ticks:
            self.stats["total_days"] = 0
            self.stats["ticked_days"] = 0
            self.stats["unticked_days"] = 0
            self.stats["current_streak"] = 0
            self.stats["longest_streak"] = 0
            return

        self.stats["total_days"] = (
            datetime.datetime.now().date() - self.ticks[0].get_date()
        ).days + 1
        self.stats["ticked_days"] = len(self.ticks)
        self.stats["unticked_days"] = (
            self.stats["total_days"] - self.stats["ticked_days"]
        )
        self.stats["current_streak"] = 0
        self.stats["longest_streak"] = 0

        current_streak = 0
        longest_streak = 0
        for tick in self.ticks:
            # if the tick is consecutive, increment the current streak
            if (
                current_streak == 0
                or (tick.get_date() - last_tick.get_date()).days == 1
            ):
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
            else:
                current_streak = 1
            last_tick = tick

        self.stats["current_streak"] = current_streak
        self.stats["longest_streak"] = longest_streak


class TerminalDisplay:
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


@click.command(
    help="""
    The streak command line tool helps you keep track of your daily streaks.\n
    It follows the "streak.txt" file format as documented in the docs/index.html.\n
    The command decides what the tool does. The possible commands are\n
    - view (default): View the streak\n
    - new: Create a new streak\n
    - mark (alias tick): Mark today's tick\n
    - list: List all the streaks in the directory
    """
)
@click.option("--dir", default=DEFAULT_STREAKS_DIR, help="Directory to store streaks")
@click.option("--file", help="Streak file to view or mark")
@click.option(
    "--name",
    help="""Name of the streak 
    (fuzzy matched, will fail if there are multiple matches or no matches)
    If the file is specified, this option is ignored""",
)
@click.argument(
    "command",
    default="view",
    required=False,
)
def streak_command(dir, file, name, command):
    """
    Streak command line tool
    """

    def get_streak_from_file_or_name(file, name):
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

    if command == "mark" or command == "tick":
        streak = get_streak_from_file_or_name(file, name)
        streak.mark_today()
    elif command == "view":
        streak = get_streak_from_file_or_name(file, name)
        display = TerminalDisplay(streak)
        display.display_all()
    elif command == "new":
        if not name:
            print("Name is required for creating a new streak")
            sys.exit(1)
        name_in_path = name.replace(" ", "-").lower()
        streak_file = os.path.join(dir, f"streak-{name_in_path}.txt")
        if os.path.exists(streak_file):
            print("Streak already exists")
        else:
            with open(streak_file, "w") as f:
                f.write(f"---\nname: {name}\ntick: Daily\n---\n")
            print(f"Streak '{name}' created")
    elif command == "list":
        files = os.listdir(dir)
        streak_files = [
            f for f in files if f.startswith("streak-") and f.endswith(".txt")
        ]
        if streak_files:
            table = Table(title="Streaks", box=box.SIMPLE)
            table.add_column("Name")
            table.add_column("Tick")
            table.add_column("Current Streak")
            table.add_column("Today's Status")

            for streak_file in streak_files:
                streak = Streak(os.path.join(dir, streak_file))
                today = datetime.datetime.now().date()
                today_status = (
                    "Ticked"
                    if any(tick.get_date() == today for tick in streak.ticks)
                    else "Not Ticked"
                )
                table.add_row(
                    streak.name,
                    streak.tick,
                    str(streak.stats["current_streak"]),
                    today_status,
                )

            console = Console()
            console.print(table)
        else:
            print("No streaks found")
    else:
        print("Command not recognized")
        sys.exit(1)


if __name__ == "__main__":
    streak_command()

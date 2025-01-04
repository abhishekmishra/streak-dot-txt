import sys
import os
import dateutil.parser
import datetime
import click
from rich.console import Console
from rich.table import Table

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

        # read yaml front matter from the file if they exist
        self.read_metadata()

        # read the ticks from the file
        self.read_ticks()

        # read the years from the ticks
        self.get_years()

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
            print(tick.tick_datetime, today_tick.tick_datetime)
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


class TerminalDisplay:
    def __init__(self, streak):
        self.streak = streak
        self.console = Console()

    def display_streak_info(self):
        """
        Display the streak information
        """
        print("Name [" + self.streak.name + "]")
        print("Tick [" + self.streak.tick + "]")

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
        first_weekday = first_day.weekday()
        num_days = (last_day - first_day).days + 1

        ticked_days = {
            tick.get_day()
            for tick in self.streak.ticks
            if tick.get_month() == first_day.month and tick.get_year() == first_day.year
        }

        table = Table(title=month_name)

        table.add_column("Sun", justify="center")
        table.add_column("Mon", justify="center")
        table.add_column("Tue", justify="center")
        table.add_column("Wed", justify="center")
        table.add_column("Thu", justify="center")
        table.add_column("Fri", justify="center")
        table.add_column("Sat", justify="center")

        week = [""] * first_weekday
        for day in range(1, num_days + 1):
            day_display = "X" if day in ticked_days else "_"
            week.append(f"{day:2} {day_display}")
            if len(week) == 7:
                table.add_row(*week)
                week = []
        if week:
            table.add_row(*week)

        self.console.print(table)


@click.command()
@click.option("--dir", default=DEFAULT_STREAKS_DIR, help="Directory to store streaks")
@click.option("--file", help="Streak file to view or mark")
@click.option(
    "--name",
    help="""Name of the streak 
    (fuzzy matched, will fail if there are multiple matches or no matches)
    If the file is specified, this option is ignored""",
)
@click.argument("command", default="view", required=False)
def streak_command(dir, file, name, command):
    """
    Streak command line tool
    """
    if file:
        streak_file = file
        streak = Streak(streak_file)
        if command == "mark" or command == "tick":
            streak.mark_today()
        elif command == "view":
            display = TerminalDisplay(streak)
            display.display_streak_info()
            display.display_streak_calendar()
        else:
            print("Command not recognized")
            sys.exit(1)
    elif name:
        # get the list of files in the directory
        files = os.listdir(dir)
        # fuzzy match the name
        matches = [f for f in files if name in f]
        if len(matches) == 0:
            print("No streaks found")
            sys.exit(1)
        elif len(matches) > 1:
            print("Multiple streaks found")
            sys.exit(1)
        else:
            streak_file = os.path.join(dir, matches[0])
            streak = Streak(streak_file)
            if command == "mark" or command == "tick":
                streak.mark_today()
            elif command == "view":
                display = TerminalDisplay(streak)
                display.display_streak_info()
                display.display_streak_calendar()
            else:
                print("Command not recognized")
                sys.exit(1)
    else:
        print("No file provided")
        sys.exit(1)


if __name__ == "__main__":
    streak_command()

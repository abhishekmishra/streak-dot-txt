import sys
import os
import dateutil.parser


class DailyTick:
    def __init__(self, date_str):
        self.date_str = date_str
        # parse ISO8601 date using dateutil.parser
        self.date = dateutil.parser.parse(date_str)

    def get_year(self):
        return self.date.year

    def get_month(self):
        return self.date.month

    def get_day(self):
        return self.date.day

    def get_weekday(self):
        return self.date.weekday()

    def get_week_in_month(self):
        # get the week in the month
        return (self.date.day - 1) // 7 + 1

    def get_week_in_year(self):
        # get the week in the year
        return self.date.isocalendar()[1]

    def __str__(self):
        return self.date


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


if __name__ == "__main__":
    print("streak.txt")

    # Get the first argument if it exists
    if len(sys.argv) > 1:
        print(sys.argv[1])
        # Check if it is a directory or a file that exists
        if os.path.isdir(sys.argv[1]):
            streak_folder = sys.argv[1]
            print("The argument is a directory -> " + streak_folder)
        elif os.path.isfile(sys.argv[1]):
            streak_file = sys.argv[1]
            print("The argument is a file -> " + streak_file)
            streak = Streak(streak_file)
            print(streak.metadata)
            print("Streak name is [" + streak.name + "]")
            print("Streak tick is [" + streak.tick + "]")
            print("Streak ticks are:")
            for tick in streak.ticks:
                print(tick.date)
            print("Streak years are:")
            print(streak.years)
        else:
            print("The argument is not a directory or file")
            exit(1)
    else:
        print("No argument provided")
        exit(1)

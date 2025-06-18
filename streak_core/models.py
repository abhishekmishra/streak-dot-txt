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
Core data models for the streak.txt format.
"""

import datetime
import dateutil.parser
from .constants import TICK_PERIODS


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
        return str(self.tick_datetime)


class Streak:
    """
    Streak class represents a streak.

    Core data model for streak management containing ticks, metadata, and statistics.

    self.period: represents the period of the tick in number of intervals.
                if the task is done once per day then period is 1
                if the task is done once per week then period is 7
                if the task is done once per month then period is the length of the month
    """

    def __init__(self, name=None, tick_type="Daily"):
        self.name = name
        self.tick = tick_type
        self.metadata = {}
        self.ticks = []
        self.years = []
        self.stats = {
            "total_days": 0,
            "ticked_days": 0,
            "unticked_days": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "tick_average": 0
        }
        
        # Set period based on tick type
        if self.tick == "Daily":
            self.period = 1
        elif self.tick == "Weekly":
            self.period = 7
        else:
            raise ValueError(f"Unsupported tick type: {self.tick}")

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
                return True
            else:
                print("Today is already ticked")
                return False
        elif self.tick == "Weekly":
            start_of_week = today - datetime.timedelta(days=today.weekday())
            week_tick = DailyTick(start_of_week.isoformat())
            if week_tick.get_week_in_year() not in [
                tick.get_week_in_year() for tick in self.ticks
            ]:
                print("Adding this week's tick:", week_tick.tick_datetime)
                self.ticks.append(week_tick)
                return True
            else:
                print("This week is already ticked")
                return False

    def get_years(self):
        """
        Get the years that the streak has been active
        """
        self.years = []
        for tick in self.ticks:
            year = tick.get_year()
            if year not in self.years:
                self.years.append(year)
        return self.years

    def add_tick(self, tick_datetime_str):
        """
        Add a new tick to the streak
        """
        tick = DailyTick(tick_datetime_str)
        self.ticks.append(tick)

    def set_metadata(self, key, value):
        """
        Set metadata for the streak
        """
        self.metadata[key] = value
        if key == "name":
            self.name = value
        elif key == "tick":
            self.tick = value

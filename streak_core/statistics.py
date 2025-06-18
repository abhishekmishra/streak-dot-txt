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
Statistics calculations for the streak.txt format.
"""

import datetime


class StreakStatsCalculator:
    """
    Calculates statistics for streak objects.
    """

    @staticmethod
    def calculate_stats(streak):
        """
        Calculate the stats for the streak

        total_days - total days the streak has been active, first tick to current date
        ticked_days - total days or weeks the streak has been ticked
        unticked_days - total days or weeks the streak has not been ticked (total_days - ticked_days)
        current_streak - current streak of ticked days or weeks
        longest_streak - longest streak of ticked days or weeks
        tick_average - percentage of days/weeks that have been ticked
        """
        if not streak.ticks:
            streak.stats = {
                "total_days": 0,
                "ticked_days": 0,
                "unticked_days": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "tick_average": 0
            }
            return streak.stats

        if streak.tick == "Daily":
            streak.stats["total_days"] = (
                datetime.datetime.now().date() - streak.ticks[0].get_date()
            ).days + 1
        elif streak.tick == "Weekly":
            streak.stats["total_days"] = (
                (datetime.datetime.now().date() - streak.ticks[0].get_date()).days // 7
            ) + 1

        streak.stats["ticked_days"] = len(streak.ticks)
        streak.stats["unticked_days"] = (
            streak.stats["total_days"] - streak.stats["ticked_days"]
        )
        
        # Calculate current and longest streaks
        current_streak, longest_streak = StreakStatsCalculator._calculate_streaks(streak)
        streak.stats["current_streak"] = current_streak
        streak.stats["longest_streak"] = longest_streak
        
        # Calculate tick average
        streak.stats["tick_average"] = (
            streak.stats["ticked_days"] / streak.stats["total_days"]
            if streak.stats["total_days"] > 0 else 0
        )

        return streak.stats

    @staticmethod
    def _calculate_streaks(streak):
        """
        Calculate current and longest streaks for the given streak object.
        Returns (current_streak, longest_streak) tuple.
        """
        current_streak = 0
        longest_streak = 0
        temp_current_streak = 0
        
        today = datetime.datetime.now().date()
        tick_dates = {tick.get_date() for tick in streak.ticks}
        last_tick_date = None

        for single_date in (
            streak.ticks[0].get_date() + datetime.timedelta(n * streak.period)
            for n in range(streak.stats["total_days"])
        ):
            if single_date in tick_dates:
                if (
                    last_tick_date is None
                    or (single_date - last_tick_date).days == streak.period
                ):
                    temp_current_streak += 1
                else:
                    temp_current_streak = 1
                if temp_current_streak > longest_streak:
                    longest_streak = temp_current_streak
                last_tick_date = single_date
            else:
                temp_current_streak = 0

        # Current streak is the streak that extends to today or the most recent date
        current_streak = temp_current_streak
        
        return current_streak, longest_streak

import unittest
import os
import datetime
from streakdottxt import Streak, DailyTick, TerminalDisplay


class TestDailyTick(unittest.TestCase):
    def test_tick_initialization(self):
        tick_str = "2025-01-05T00:00:00"
        tick = DailyTick(tick_str)
        self.assertEqual(tick.tick_datetime_str, tick_str)
        self.assertEqual(tick.get_year(), 2025)
        self.assertEqual(tick.get_month(), 1)
        self.assertEqual(tick.get_day(), 5)


class TestStreak(unittest.TestCase):
    def setUp(self):
        self.test_dir = "/tmp/test_streaks"
        os.makedirs(self.test_dir, exist_ok=True)
        self.streak_file = os.path.join(self.test_dir, "streak-test.txt")
        with open(self.streak_file, "w") as f:
            f.write(
                "---\nname: Test Streak\ntick: Daily\n---\n2025-01-01T00:00:00\n2025-01-02T00:00:00\n"
            )

    def tearDown(self):
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

    def test_read_metadata(self):
        streak = Streak(self.streak_file)
        self.assertEqual(streak.name, "Test Streak")
        self.assertEqual(streak.tick, "Daily")

    def test_read_ticks(self):
        streak = Streak(self.streak_file)
        self.assertEqual(len(streak.ticks), 2)
        self.assertEqual(streak.ticks[0].get_date(), datetime.date(2025, 1, 1))

    def test_mark_today(self):
        streak = Streak(self.streak_file)
        streak.mark_today()
        self.assertEqual(len(streak.ticks), 3)
        self.assertEqual(streak.ticks[-1].get_date(), datetime.datetime.now().date())

    def test_calculate_stats(self):
        streak = Streak(self.streak_file)
        streak.calculate_stats()
        self.assertEqual(
            streak.stats["total_days"],
            (datetime.datetime.now().date() - datetime.date(2025, 1, 1)).days + 1,
        )
        self.assertEqual(streak.stats["ticked_days"], 2)


class TestTerminalDisplay(unittest.TestCase):
    def setUp(self):
        self.test_dir = "/tmp/test_streaks"
        os.makedirs(self.test_dir, exist_ok=True)
        self.streak_file = os.path.join(self.test_dir, "streak-test.txt")
        with open(self.streak_file, "w") as f:
            f.write(
                "---\nname: Test Streak\ntick: Daily\n---\n2025-01-01T00:00:00\n2025-01-02T00:00:00\n"
            )
        self.streak = Streak(self.streak_file)
        self.display = TerminalDisplay(self.streak)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

    def test_display_streak_info(self):
        self.display.display_streak_info()

    def test_display_streak_stats(self):
        self.display.display_streak_stats()

    def test_display_streak_calendar(self):
        self.display.display_streak_calendar()


if __name__ == "__main__":
    unittest.main()

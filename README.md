# Streak.txt

If you 🫵 too repeat certain mundane tasks daily as part of a practice or routine and want to track it in the simplest possible way, you're at the right place! 

> What about your vomit streak? Jerry Seinfeld : I know! I haven't thrown up since June 29, 1980!
> 
> [Jerry Seinfeld - The Dinner Party](https://www.imdb.com/title/tt0697684/characters/nm0000632#:~:text=What%20about%20your%20vomit%20streak,up%20since%20June%2029%2C%201980!)

*Streak.txt* is a simple file format to track streaks (or lack thereof) of repeated tasks. Something like this -> 
✅✅✅⛔✅⛔✅

All your streaks are in future-proof plain text files on your disk. If you complete a task today append its date, if you didn't then don't enter anything.

Here's a sample:
(notice the miss on 2nd Jan 2025)

```
---
name: Jumping Jacks
---
2021-01-01
2021-01-03
2021-01-04
```

## Getting started

```
git clone https://github.com/abhishekmishra/streak-dot-txt.git
cd streak-dot-txt
pip install -r requirements.txt
python streakdottxt.py --help
```

## Docs

Details about the file format and usage of the tool are here [Streak.txt Docs](https://abhishekmishra.github.io/streak-dot-txt/)
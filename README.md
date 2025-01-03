# streak.txt
We define a  simple file format for managing streaks (and gaps) of repeated
occurences. This format has similar goals as the todo.txt file format.

## Goals of the project

1. Track one streak per file.
1. Changes to file are append only.
1. Each streak file has some metadata.
1. We can specify a name for the streak such as "Draw daily".
1. We can specify the period of the streak such as "Monthly" or "Weekly".
1. We can specify the tick of the streak such as "Daily" or "Hourly". The tick
   has to be a smaller time measure than the period.
1. We can specify the expected frequency of the streak such as "10 times", "7
   times" etc.
1. No entry is required when task is not done. In fact a missing entry qualifies
   as "Not done".
1. We can specify an optional quantity when making an entry when task is done.
1. We can specify an optional comment when making an entry.
1. The comment can contain hyperlinks.

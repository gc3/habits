# Habits

Habit tracking CLI using CSV files for storage and Todoist for recurring task
management.

The goal is let one use the same system on iOS, MacOS, and Linux by just
putting tracking files in a cloud storage system.

## Installation
```
git clone ...habits.git
cd habits
make install
```

## Usage
usage: habits [-h] [-c C | -n | -d | -r | -u | -l | -s | -a] [habit]

positional arguments:
  habit

options:
  -h, --help  show this help message and exit
  -c C        [c]omplete the given habit today
  -n          create a [n]ew habit to track
  -d          [d]elete the given habit
  -r          a[r]chive the given habit
  -u          [u]n-archive the given habit
  -l          [l]ist habits being tracked
  -s          show the [s]treaks / [s]tats of tracked habits
  -a          list [a]ll the habits including archived ones

## Configuration
Use ~/.habitsrc (or update CONFIG_FILE) to tell this library where to store its
data for habits and (optionally) the Todoist API Key to enable that integration.

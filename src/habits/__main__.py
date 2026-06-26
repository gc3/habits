# ----------- Main/CLI ---------------------------------------------------------
"""
  Habit tracking CLI using CSV files for storage and Todoist for recurring task
  management.
"""
# pylint: disable=too-many-branches

import sys
import argparse
import setproctitle

from habits import tracker

setproctitle.setproctitle("habits")

def parse_cli():
  """
    return parsed CLI arguments
  """

  # optional arguments to define actions on a given habit
  habit_args = [
    ["-c", "store",       "[c]omplete the given habit today"],
    ["-n", "store_true",  "create a [n]ew habit to track"],
    ["-d", "store_true",  "[d]elete the given habit"],
    ["-r", "store_true",  "a[r]chive the given habit"],
    ["-u", "store_true",  "[u]n-archive the given habit"],
  ]

  # optional arguments that DO NOT want a habit (like -h)
  loner_args = [
    ["-l", "store_true",  "[l]ist habits being tracked"],
    ["-s", "store_true",  "show the [s]treaks / [s]tats of tracked habits"],
    ["-a", "store_true",  "list [a]ll the habits including archived ones"],
  ]

  # add the habit to work on if it's there
  parser = argparse.ArgumentParser(prog = "habits", description = __doc__)
  parser.add_argument("habit", nargs='?')

  # add all the optional arguments
  group = parser.add_mutually_exclusive_group()
  for flag, action, helptext in habit_args + loner_args:
    group.add_argument(flag, action=action, help=helptext)

  parsed = parser.parse_args()

  # make sure the habit is included for the flags that require it
  habit_flags = [opt[0].lstrip('-') for opt in habit_args]
  flags_used = any(getattr(parsed, flag) for flag in habit_flags)
  if not parsed.habit and flags_used:
    parser.error("You must add the [habit] positional argument.")

  return parsed


def main():
  """
    main, main go away. come again another day.
  """

  #  Handle the 'loner' flags as defined in the parser:
  #    - If the args have -l or -h or -s, we ignore all other args.
  #    - If there's no args at all, just print the list of habits
  args = parse_cli()
  assert args is not None

  if args.l or (len(sys.argv) == 1):
    # get a list of all the currently tracked habits
    names = tracker.get_all_habit_names(include_archived=False)[0]
    print("Current Habits\n" + "\n".join(f" - {name}" for name in names))
    return

  if args.s:
    # print the stats for all the habits
    stats = tracker.get_all_habit_stats()
    print("Habit Stats\n" + "\n".join(f" - {s}" for s in stats))
    return

  if args.a:
    # print the stats for all the habits
    names = tracker.get_all_habit_names(include_archived=True)
    print("Current Habits\n" + "\n".join(f" - {name}" for name in names[0]))
    print("\nArchived Habits\n" + "\n".join(f" - {name}" for name in names[1]))
    return

  # Handle the 'habit' flags as defined in the parser:
  #    - we require a habit name
  #    - If there's no optional args & there is a habit name, we print it's info
  assert args.habit is not None

  habit = tracker.HabitTracker(args.habit)
  if habit is None:
    print(f"  error: failed to load habit '{args.habit}'")
    return

  if args.c:
    # complete the named habit today for any date today or older
    if habit.complete(args.c, today_only=False):
      print(f"Habit '{args.habit}' completed today!")
    else:
      print(f"  error: Failed to complete '{args.habit}'. Does it exist?")

  elif args.n:
    # create a new habit for tracking
    if habit.create():
      print(f"New habit '{args.habit}' created!")
    else:
      print(f"  error:Failed to create '{args.habit}'. Does it exist?")

  elif args.d:
    # delete the named habit from tracking
    resp =input(f"Really delete the habit '{args.habit}'? (y/n) ")
    if resp.strip().lower() in ('y','yes'):
      habit.delete()
      print(f"Habit '{args.habit}' deleted and removed from tracking.")

    else:
      print("Canceling deletion")

  elif args.r:
    # archive this habit
    if habit.archive():
      print(f"Habit '{args.habit}' archived.")
    else:
      print(f"  error:Failed to archive '{args.habit}'")

  elif args.u:
    # un-archive this habit
    if habit.unarchive():
      print(f"Habit '{args.habit}' un-archived!")
    else:
      print(f"  error:Failed to un-archive '{args.habit}'")

  else:
    # give detailed info about a habit
    print(str(habit))


if __name__ == "__main__":
  main()

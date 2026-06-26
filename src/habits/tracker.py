## ----------- Habit Tracker ----------------------------------------------------
"""
  Backend for habit tracking. This reads and writes the needed CSV and config
  files to store and retrieve a desired habit. An instance of HabitTracker
  tracks a single habit at a time.
"""

import os

from calendar import Calendar
from datetime import date, datetime, timedelta
try:
  from todoist_api_python.api import TodoistAPI
  HAS_TODOIST = True
except ImportError:
  HAS_TODOIST = False

from habits import csvutils
from habits import config

_DEFAULT_COLUMNS = ['date', 'count']
_DEFAULT_DATE_FMT = csvutils.DEFAULT_DATE_FMT

def get_all_habit_names(include_archived=False):
  """
    return a list of every habit being tracked by checking the habit
    storage directly
  """
  cfg = config.parse_config()
  storage_dir = config.DEFAULT_STORAGE_DIR
  if cfg:
    storage_dir = cfg.get('storage_dir', config.DEFAULT_STORAGE_DIR)

  config.ensure_storage(storage_dir)

  names = os.listdir(storage_dir)
  curr = [os.path.splitext(f)[0] for f in names if f.lower().endswith(".csv")]

  arch = []
  if include_archived:
    names = os.listdir(os.path.join(storage_dir, config.ARCHIVED_STORAGE_DIR))
    arch = [os.path.splitext(f)[0] for f in names if f.lower().endswith(".csv")]

  return (curr, arch)

def get_all_habit_stats():
  """
    return formatted stats for all the habits being tracked
  """
  stats = []

  names = get_all_habit_names()[0]
  for name in names:
    habit = HabitTracker(name)
    stats.append(f"{name:15}\n{habit.get_stats_string()}")

  return stats

class HabitTracker:
  """
    A habit is a task one repeats often. This handles tracking and storing it.
  """
  def __init__(self, name, task_id=None):
    self.name_ = name
    self.task_id_ = task_id

    # load what we need from the config file or use defaults
    cfg = config.parse_config()
    if cfg is not None:
      self.api_token_ = cfg.get('api_token', None)
      storage_dir = cfg.get('storage_dir', config.DEFAULT_STORAGE_DIR)

    else:
      self.api_token_ = None
      storage_dir = config.DEFAULT_STORAGE_DIR

    config.ensure_storage(storage_dir)
    self.file_path_ = os.path.join(storage_dir, f"{self.name_}.csv")
    self.archive_path_ = os.path.join(
      storage_dir,
      config.ARCHIVED_STORAGE_DIR,
      f"{self.name_}.csv"
    )

    # set up the storage handling
    self.model_ = csvutils.CSVEditor(self.file_path_, _DEFAULT_DATE_FMT)
    assert self.model_ is not None

  def __repr__(self):
    """
      Print me !
    """
    output = f"Habit Tracking data for '{self.name_}'\n"

    dedup = {}
    two_weeks_ago = date.today() - timedelta(days=14)
    rows = self.model_.load()
    for row in rows:
      assert row
      day = datetime.strptime(row[0], _DEFAULT_DATE_FMT).date()
      if two_weeks_ago <= day < date.today():
        dedup[day] = True

    output += (
      f"  Days Completed:\n"
      f"    \t{len(rows)} total\n"
      f"    \t{len(dedup)} of previous 14\n"
      f"  Stats:\n{self.get_stats_string()}"
    )

    if self.task_id_:
      output += "\n  Todoist Task: " + self.task_id_

    return (
      f"{output}\n"
      f"  Calendar View:\n"
      f"  {self.get_cal_view()}\n"
      f"  File: {str(self.file_path_)}"
    )

  def complete(self, row_data, today_only=True):
    """
      Update this habit as complete for today. If this habit is using a
      recuring task, also mark it as complete for the day.

      Returns False if we're trying to complete a habit that doesnt already
      exist, True otherwise.
    """
    if not self.model_.verify():
      return False

    if not isinstance(row_data, list):
      row_data = [row_data]

    # store today's completion in the backing store
    self.model_.append(row_data)

    # let our task tracker know we completed today's habit by updating
    # the recurring task for it and updating the streak count for it
    if (HAS_TODOIST and (self.api_token_ is not None) and (self.task_id_ is not None)):
      api = TodoistAPI(self.api_token_)
      task = api.get_task(self.task_id_)
      today = datetime.now().date()

      if ((not today_only) or              # always mark complete
          (task.due.date.date() <= today)): # only mark complete if it's today
        text = "Your current streak is " + str(self.get_streak()) + " days!"
        api.update_task(self.task_id_, description=text)
        api.complete_task(self.task_id_)

    return True

  def create(self):
    """
      create this habbit's storage. true if it works, false if not.
    """
    return self.model_.create(_DEFAULT_COLUMNS)

  def delete(self):
    """
      remove this habit from tracking and delete it's storage on disk
    """
    self.model_.destroy()

    # delete in the task tracker if relevant
    if HAS_TODOIST and (self.api_token_ is not None) and (self.task_id_ is not None):
      api = TodoistAPI(self.api_token_)
      api.delete_task(self.task_id_)

  def archive(self):
    """
      move this habit to the archive
    """
    os.rename(self.file_path_, self.archive_path_)

    # complete the task forever in the task tracker
    if (self.api_token_ is not None) and (self.task_id_ is not None):
      api = TodoistAPI(self.api_token_)

      if (not api.complete_task(self.task_id_) or
          not api.update_task(self.task_id_, due_string="no date")):
        return False

    return True

  def unarchive(self):
    """
      grab this habit from the archive and return it to current status
    """
    os.rename(self.archive_path_, self.file_path_)

    # re-open the task so it can be easily tracked again
    if (self.api_token_ is not None) and (self.task_id_ is not None):
      api = TodoistAPI(self.api_token_)

      if (not api.uncomplete_task(self.task_id_) or
          not api.update_task(self.task_id_, due_string="every day at noon")):
        return False

    return True

  def get_stats_string(self):
    """
      return a formatted string of the stats for this habit to make printing
      easier
    """
    days = self.get_days_per_completion()
    return (
      f"\t{self.get_streak():>6d} day streak\n"
      f"\t{self.get_count_per_instance():>6.2f} count per instance\n"
      f"\t{self.get_count_per_day():>6.2f} count per day\n"
      f"\t{days:>6.2f} avg days per completion\n"
      f"\t{0 if days == 0 else 7 / days:>6.2f} avg completions per week"
    )

  def get_cal_view(self):
    """
      return a string containing a calendar view for this month with an X for
      each day the habit was done
    """

    # grab all the data, filter it for dates in the current month
    now = datetime.now().date()
    data = self.model_.load()
    dates = [datetime.strptime(row[0], _DEFAULT_DATE_FMT) for row in data]
    done_days = [d.day for d in dates if d.month == now.month]

    # format the calendar into a string for the caller
    output = "\tSu Mo Tu We Th Fr Sa"

    for week in Calendar(firstweekday=6).monthdayscalendar(now.year, now.month):
      nums = []
      comp = []

      for d in week:
        if d == 0:
          # blank days are left blank
          nums.append("   ")
          comp.append("   ")
        else:
          # put the day of the month above the completion indicator
          nums.append(f"\033[93m{d:02}\033[0m " if d == now.day else f"{d:02} ")

          # put an X for days the habit was completed - otherwise
          comp.append(" X " if d in done_days else " - ")

      output += "\n\t" + "".join(nums)
      output += "\n\t" + "".join(comp)

    return output

  def get_count_per_instance(self):
    """
      calculate and return the average value per habit completion if the data
      is an ingeger. "Not a Number" or nan, if not.
    """
    total = 0
    rows = self.model_.load()

    for row in rows:
      try:
        data = row[1]
        total += float(data)
      except ValueError:
        # that's not an int!
        return float('nan')

    completions = len(rows)
    return 0 if completions == 0 else total / completions

  def get_count_per_day(self):
    """
      calculate and return the average value per DAY COMPLETED if the data
      is an ingeger. "Not a Number" or nan, if not.
    """
    total = 0
    days = set()
    rows = self.model_.load()

    for row in rows:
      try:
        days.add(row[0])        # day
        total += float(row[1])  # data
      except ValueError:
        # that's not an int!
        return float('nan')

    ndays = len(days)         # unique num of days in the data
    return 0 if ndays == 0 else total / ndays


  def get_days_per_completion(self):
    """
      calculate and return the avg number of days between completions
    """
    rows = self.model_.load()
    completions = len(rows)

    if completions != 0:
      first = datetime.strptime(rows[0][0], _DEFAULT_DATE_FMT).date()
      last = datetime.strptime(rows[len(rows) - 1][0], _DEFAULT_DATE_FMT).date()
      return ((last - first).days + 1) / completions

    return 0

  def get_streak(self):
    """
      calculate and return the current habit streak in number of days
    """
    streak = 0
    current = datetime.now().date()

    for row in reversed(self.model_.load()):
      day = datetime.strptime(row[0], _DEFAULT_DATE_FMT).date()

      if day == current:
        streak += 1
        current -= timedelta(days=1)

      elif day < current:
        break  # streak broken

    return streak

# ----------- CSV Utilities ----------------------------------------------------
"""
  Useful wrappers around csv handling
"""

import os
import csv
from datetime import datetime

DEFAULT_DATE_FMT = "%Y-%m-%d %H:%M"
DEFAULT_HEADER_ROW = ['date', 'data']

class CSVEditor:
  """
    Handle the editing of a CSV
  """
  def __init__(self, file_path, date_fmt=DEFAULT_DATE_FMT):
    self.path_ = file_path
    self.rows_ = None
    self.date_fmt_ = date_fmt

  def get_row_from_user_input(self, queries):
    """
      gather user input in order to create a row to write to the CSV
    """
    return [input(query) or default for query, default in queries.items()]

  def verify(self):
    """
      tells you if the storage is 'okay'. for example, that it exists
    """
    assert self.path_ is not None
    return os.path.exists(self.path_)

  def append(self, row, add_date=True):
    """
      Store the given row. Optionally add the current date to the saved row
    """

    # add today's date if requested
    if add_date:
      today = datetime.now().strftime(self.date_fmt_)
      row = [today] + row

    # and append the row to the file
    with open(self.path_, "a+", newline="", encoding="utf-8") as f:
      writer = csv.writer(f, lineterminator="\n")
      writer.writerow(row)

    return True

  def create(self, header_row=DEFAULT_HEADER_ROW):
    """
      create the file for storage if it doesnt exist and return True, false
      otherwise
    """
    if not self.verify():
      self.append(header_row, add_date=False)
      return True

    return False

  def destroy(self):
    """
      destroy the CSV file if it exists
    """
    if self.verify():
      os.remove(self.path_)

  def load(self, use_cache=True):
    """
      read the CSV file into memory. returns the rows read
    """
    if not self.verify():
      raise FileNotFoundError(f"Failed to load data for '{self.path_}'.")

    # use cached data if the caller wants it
    if self.rows_ is not None and use_cache is True:
      return self.rows_

    # load the file data from disk
    with open(self.path_, newline="") as f:
      reader = csv.reader(f)

      # skips the column titles in the first row and all blank rows
      self.rows_ = list(filter(None, list(reader)[1:]))

    return self.rows_

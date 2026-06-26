# Habits

Habit tracking CLI using CSV files for storage and Todoist for recurring task
management.

The goal is let one use the same system on iOS, MacOS, and Linux by just
putting tracking files in a cloud storage system.

## Installation
```sh
git clone git@github.com:gc3/habits.git
cd habits
make install
```

## Usage
```sh
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
```

## Configuration

Configuration is optional. With no config file, habits stores data under
`$XDG_DATA_HOME/habits` (default `~/.local/share/habits`) and the Todoist
integration stays off.

To change defaults, create `$XDG_CONFIG_HOME/habits/habitsrc` (default
`~/.config/habits/habitsrc`). It's a plain `key = value` file — no section
header needed:

```ini
storage_dir = ~/Dropbox/habits
api_token_file = ~/.local/state/habits/token
```

- **`storage_dir`** — where the per-habit CSV files live. An `.archive/`
  subdirectory is created alongside them. Both are created automatically if
  missing. Point this at a synced folder (Dropbox, iCloud Drive, etc.) to use
  the same habits across iOS, macOS, and Linux.
- **`api_token_file`** — path to a file containing your Todoist API token,
  which enables the recurring-task integration. The config stores the *path*,
  not the token itself, so the secret can live outside a (possibly public)
  dotfiles repo. The file is just the raw token on one line:

Get your Todoist API token from Todoist -> Settings -> Integrations ->
Developer -> API token. If `api_token_file` is set but unreadable, habits fails
loudly rather than silently skipping sync.

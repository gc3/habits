# iOS Shortcuts

A set of Apple Shortcuts for logging and reading habits from iOS/iPadOS (and
macOS) when the habit CSV files live in a synced folder — e.g. iCloud Drive or
Dropbox pointed at by `storage_dir` in `~/.config/habits/habitsrc`. The
shortcuts read and write the same CSV format the `habits` CLI uses, so the two
stay interchangeable across devices.

## Files

| File | Role |
| --- | --- |
| `Habits_Habit_Reader.shortcut` | Reads a habit's CSV and shows its recent entries |
| `Habits_Habit_Writer.shortcut` | Appends a completion row to a habit's CSV |

These are the signed `.shortcut` exports straight from the Shortcuts app — the
same files that import on an iPhone/iPad/Mac. They're self-contained and don't
depend on an iCloud link staying alive, but they are opaque binaries (no
readable diff in git). A readable markdown breakdown of each shortcut's actions
can be added later from an unsigned `.plist`/XML export — see "Readable source"
below.

The `.shortcut` files are signed (Apple Encrypted Archive), so their logic
isn't reviewable in git. To add a diff-friendly breakdown, export each shortcut
as an unsigned `.plist`/XML (e.g. a RoutineHub source tool, or the macOS
`shortcuts` CLI) and commit that alongside — a markdown step list per shortcut
makes the action flow reviewable without installing anything.

## Installation

1. Get the `.shortcut` file onto an Apple device (AirDrop, iCloud Drive, or just
   download it from this repo on the device).
2. Open it. It launches the Shortcuts app and shows the actions for review.
3. Scroll through, then tap **Add Shortcut**.
4. On first run it asks where your habits live (see "Pointing at your folder").

The shortcuts don't hardcode a path — each uses an **import question** so the
first run asks which folder holds your habit CSVs. Point it at the same synced
folder `storage_dir` references in `~/.config/habits/habitsrc` (iCloud Drive,
Dropbox, etc.) and the shortcuts and the `habits` CLI operate on the same files.

## CSV format contract

The shortcuts read and write the same per-habit CSV files as the `habits` CLI.
The format — file layout, the `date,count` header, etc — is documented once in the
[Data format section of the main README](../README.md#data-format).

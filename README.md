# Smart File Organizer

A friendly toolbox for tidying and looking after your files - **safely**.
Every tool shows a **preview** first, asks before changing anything, never overwrites,
never deletes, and (for anything that moves or renames files) can be **undone**.
It also explains what your files (`.jpeg`, `.svg`, `.pdf` ...) and folders mean.

```
Before                          After
  report.pdf                      Documents/report.pdf
  holiday.mp4                     Videos/holiday.mp4
  logo.svg                        Images/logo.svg
  setup.msi                       Installers/setup.msi
  movie.mp4.crdownload            (left alone - still downloading!)
  Your own folders                (never touched)
```

---

## The easy way (no commands to learn)

**Windows:** double-click **`START_HERE.bat`**
**Mac / Linux:** double-click **`start.command`** (Mac: first time, right-click > Open)

Then type a number and press **Enter**. That's it.
No Python? The launcher tells you where to get it (python.org, free).

```
   1.  Tidy a folder into category folders
   2.  Rename many files at once
   3.  Archive old files
   4.  Find duplicate files
   5.  Remove empty folders
   6.  What is using my disk space?
   7.  Show a folder as a tree
   8.  Back up a folder (zip)
   9.  Check files weren't changed
  10.  Undo the last change
  11.  What does a file type mean?
  12.  Learn the basics
  13.  Fix old '.txt / .mp4' folders
   0.  Exit
```

### How to choose a folder (3 ways)
Whenever a tool asks "which folder?", you get this list:

1. **Downloads / Desktop / Documents** - just type its number.
2. **Browse...** - a normal window opens; click your folder (any drive, e.g. `D:\Organizer`) and press OK.
   *(If the window seems missing, check the taskbar - it can open behind the black window.)*
3. **Type or paste a path:**
   - **Windows:** open the folder in File Explorer, click the address bar, press `Ctrl+C`.
     In the organizer window **right-click** (that pastes) and press Enter.
     Or **drag the folder into the window**.
   - **Mac:** drag the folder into the Terminal window and press Enter.

### "Windows protected your PC" / "Publisher could not be verified"
This appears for any `.bat` file that isn't digitally signed - it is normal for downloaded
scripts. Click **Run**. You can open `START_HERE.bat` in Notepad first to see it only
starts `python\toolbox.py`. To stop the warning for good: right-click the **.zip** file >
Properties > tick **Unblock** > OK, *then* extract it.

---

## Use it from ANY folder: the `start_here` command

Install a global command **once**, then start the toolbox from wherever you are.

**Install (once):** double-click **`INSTALL_COMMAND.bat`**, then close that window.
(Mac/Linux: `python3 python/install_command.py`.) No admin rights needed.

**Use it:**
1. Open the folder you want to tidy in File Explorer.
2. Click the **address bar**, type `cmd` (or `powershell`) and press **Enter**.
3. Type **`start_here`** and press Enter.

The toolbox opens and **"This folder"** is already selected - just press Enter at
every "which folder?" question.

```
 1.  This folder  (D:\Downloads\Stuff)  - just press Enter
 2.  Browse...
 3.  Type or paste a folder path
```

Extras:
- `start_here "D:\Inbox"` - use a specific folder instead.
- `start_here --plain` - no colours or animations.
- Prefer another name? `python python/install_command.py --name tidy`
- Remove it: double-click **`UNINSTALL_COMMAND.bat`**.
- If you move the project folder, run the installer again.

> The installer only adds one small launcher file - to `%LOCALAPPDATA%\Microsoft\WindowsApps`
> (already on your PATH, so it works straight away), or to a private folder it adds to
> *your* PATH if that isn't possible.

**Something not working? Double-click `CHECK_COMMAND.bat`.**
It tests the command and tells you in plain words what to do. The usual cause is a
terminal that was opened *before* the install (or from File Explorer's address bar), which
keeps an old PATH. Fixes, easiest first:
1. Run `INSTALL_COMMAND.bat` again (it now puts the command in a folder Windows already
   searches, so it normally works immediately).
2. Open a fresh terminal from the **Start menu** and `cd` to your folder.
3. Sign out of Windows and back in once.
4. Last resort, no install needed: `python D:\path\to\smart-file-organizer\python\toolbox.py --here`

Built-in protections:
- The launcher keeps working if Python is updated or moved (it falls back to `py -3` / `python`).
- If you move the project folder, typing `start_here` says so and tells you to re-run the installer.
- A Python that is too old, or the Microsoft Store "python" stub, gives a clear message instead of a crash.
- If a tool hits an error, the toolbox shows a friendly message, saves details to `last_error.txt`
  and returns to the menu - the window never just disappears.

---

## What each tool does

| # | Tool | In plain words | File |
|---|---|---|---|
| 1 | **Tidy** | Sorts loose files into `Images/`, `Documents/`, `Videos/` ... and explains each folder and file type in the preview | `easy_organizer.py` / `smart_organizer.py` |
| 2 | **Rename** | Rename lots of files at once: lowercase, no spaces, date first, numbered (`trip_001.jpg`), add/replace text | `rename_files.py` |
| 3 | **Archive old files** | Moves files you haven't touched in a year (you choose) into `_Old/<year>/` | `archive_old_files.py` |
| 4 | **Duplicates** | Finds exact copies; optionally moves the extras aside for you to review. Never deletes | `find_duplicates.py` |
| 5 | **Empty folders** | Removes folders with nothing inside | `cleanup_empty_folders.py` |
| 6 | **Disk report** | Where did my space go? Sizes per category, biggest files, stale files | `disk_report.py` |
| 7 | **Folder tree** | A picture of what's inside a folder and how big each part is | `folder_tree.py` |
| 8 | **Backup** | A dated `.zip` copy of a folder, checked afterwards | `backup_folder.py` |
| 9 | **Checksums** | Save "fingerprints" of files now, check later that nothing changed or got damaged | `checksum_tool.py` |
| 10 | **Undo** | Reverses the last change made by tidy, rename, archive, duplicates or migrate | `common.py` (used by all) |
| 11-12 | **Look up / Learn** | What does `.svg` mean? What is a folder? What is undo? | `explain.py` |
| 13 | **Fix old folders** | Converts the old `.txt` / `.mp4` folders from the first script | `migrate_old_folders.py` |

> Read-only tools (disk report, tree, checksums, duplicates report) never change your files.

---

## What do file types and folders mean?

- In the app: **11. What does a file type mean?** - type `svg`, `.jpeg` or `photo.HEIC`.
- The preview screen explains every type it found.
- A full glossary is in **[docs/GLOSSARY.md](docs/GLOSSARY.md)**
  (rebuild it with `python python/explain.py --markdown > docs/GLOSSARY.md`).

| Type | Meaning |
|---|---|
| `.jpg` / `.jpeg` | Same thing - the common photo format |
| `.png` | Sharp image, can be see-through (screenshots, logos) |
| `.svg` | Drawing made of shapes - stays sharp at any size; opens in a browser |
| `.pdf` | Document that looks the same everywhere |
| `.zip` | Many files squeezed into one |
| `.exe` / `.msi` | Programs / installers - only run ones you trust |

| Folder | Holds |
|---|---|
| `Images/` | Pictures, photos, screenshots, icons |
| `Documents/` | PDFs, Word files, notes, e-books |
| `Videos/` `Audio/` | Movies, clips / music, voice notes |
| `Archives/` | Zip and other compressed bundles |
| `Installers/` | App installers |
| `Other/` | Types the tool doesn't know yet - nothing is wrong with them |
| `_Duplicates/`, `_Duplicates_Review/` | Exact copies, safe to review and delete |
| `_Old/<year>/` | Files not touched for a long time |

---

## Project layout

```
smart-file-organizer/
├── README.md
├── LICENSE                            MIT
├── START_HERE.bat                     Windows: double-click me
├── start.command                      Mac/Linux: double-click me
├── INSTALL_COMMAND.bat                installs the global `start_here` command
├── UNINSTALL_COMMAND.bat              removes it again
├── CHECK_COMMAND.bat                  tests the command and explains any problem
├── config/categories.json             which extension goes in which folder (edit me)
├── docs/GLOSSARY.md                   what every file type and folder means
├── python/                            Python 3.8+, no dependencies
│   ├── toolbox.py                     THE MENU - start here
│   ├── install_command.py             creates the global `start_here` command
│   ├── easy_organizer.py              guided tidy-up, undo, look-up, learn
│   ├── smart_organizer.py             power-user command-line organizer
│   ├── rename_files.py                bulk rename (with undo)
│   ├── archive_old_files.py           move old files into _Old/<year>
│   ├── find_duplicates.py             find identical files, quarantine the extras
│   ├── cleanup_empty_folders.py       remove empty folders
│   ├── disk_report.py                 what is using my disk space?
│   ├── folder_tree.py                 folder picture with sizes
│   ├── backup_folder.py               dated zip backup
│   ├── checksum_tool.py               fingerprints: did anything change?
│   ├── migrate_old_folders.py         old ".txt/.mp4" folders -> categories
│   ├── explain.py                     plain-English file type / folder explanations
│   ├── ui.py                          colours, spinner, progress bar, menus
│   └── common.py                      shared helpers + the undo system
└── tests/
    ├── test_smart_organizer.py        organizer, migrate, explain
    ├── test_tools.py                  all the other tools + undo
    ├── test_install.py                the global command + 'This folder'
    └── test_toolbox.py                the toolbox survives errors
```

## Safety

| Risk | Protection |
|---|---|
| Changing something by mistake | Preview first; nothing happens until you say yes |
| Breaking a running download | `.crdownload .part .tmp ...` skipped, and files changed in the last 5 minutes |
| Overwriting a file | Name clashes become `name (1).ext` |
| Deleting a file | **No tool deletes files.** (Only truly empty folders can be removed.) |
| System files | Hidden/system files are skipped |
| Your own folders | Only loose files are touched; sub-folders are left alone |
| Running on `C:\` | Drive roots are refused |
| "Where did my file go?" | Each change writes `.organizer_logs/<tool>_*.json`; **Undo** reverses it |

Files without an extension (e.g. `Makefile`) are left alone by the organizer.
One Undo works for every tool: tidy, rename, archive, duplicates and migrate.
(Removed empty folders are not restored - there was nothing in them.)

---

## For power users: one-line commands

Each tool also works with plain commands. Replace the path with yours.
Every tool has `--help`.

```bash
python python/smart_organizer.py "C:\Users\you\Downloads" --dry-run   # preview
python python/smart_organizer.py "C:\Users\you\Downloads"             # run (asks first)
python python/smart_organizer.py "C:\Users\you\Downloads" --undo      # undo anything

python python/rename_files.py "C:\Users\you\Pictures" --lower --spaces --only "*.jpg"
python python/rename_files.py "C:\Users\you\Pictures" --number holiday
python python/archive_old_files.py "C:\Users\you\Downloads" --days 180
python python/find_duplicates.py "C:\Users\you\Downloads" --min-size 100
python python/find_duplicates.py "C:\Users\you\Downloads" --move-to "C:\Users\you\_dupes"
python python/cleanup_empty_folders.py "C:\Users\you\Downloads" --dry-run
python python/disk_report.py "C:\Users\you\Downloads" --top 15 --stale-days 365
python python/folder_tree.py "C:\Users\you\Downloads" --depth 3 --files
python python/backup_folder.py "C:\Users\you\Documents" --dest "D:\Backups"
python python/checksum_tool.py create "D:\Backups"
python python/checksum_tool.py verify "D:\Backups"
python python/migrate_old_folders.py "C:\Users\you\Downloads" --dry-run
```

### smart_organizer.py options

| Option | What it does |
|---|---|
| `--dry-run` | Show the plan; change nothing |
| `-y`, `--yes` | Don't ask for confirmation (scheduled use) |
| `--mode category / extension / date / category-date` | How folders are named |
| `--min-age MINUTES` | Skip files modified in the last N minutes (default 5) |
| `--dedupe` | Exact copies go to `_Duplicates/` |
| `--exclude PATTERN` | Leave matching files alone, e.g. `--exclude "*.psd"` (repeatable) |
| `--include-hidden` | Also move hidden files |
| `--config FILE` | Use your own categories JSON |
| `--undo` / `--undo-log FILE` | Reverse the last change / a specific one |

### Customising categories

Edit `config/categories.json`:

```json
{
  "other_folder": "Other",
  "categories": {
    "Images": [".jpg", ".png", ".webp"],
    "Ebooks": [".epub", ".mobi"]
  },
  "skip_extensions": [".crdownload", ".part", ".tmp"],
  "skip_names": ["desktop.ini", "thumbs.db"]
}
```

Unlisted extensions go to `other_folder`. If you pass `--config`, the keys you give
**replace** the defaults, so include the full `categories` list you want.
Every tool reads this same file.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Troubleshooting

- **Window closes instantly:** use the launcher files - they keep the window open.
- **Colours look like `[36m`:** run `python python/toolbox.py --plain`.
- **"Python not found":** install it from python.org and tick "Add Python to PATH".
- **Not sure what a file is?** Menu 11 explains it.

## Not included

The optional Windows-only extras from earlier versions (`powershell/` and `batch/`
scripts, such as the daily Task Scheduler job) are not part of this bundle. If you have
them, drop those two folders in next to `python/`. They don't depend on anything here
except `config/categories.json`. The Python tools above cover everything they did.

## Contributing

Ideas welcome: new categories, new tools, bug reports. Keep the scripts
dependency-free and add a test for any behaviour change.

## License

MIT - see `LICENSE`.

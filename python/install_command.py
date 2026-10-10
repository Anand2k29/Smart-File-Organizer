#!/usr/bin/env python3
"""
install_command.py - create a GLOBAL command so you can start the toolbox from ANY folder.

    python install_command.py                install the command  "start_here"
    python install_command.py --check        test it and explain any problem
    python install_command.py --name tidy    use a different command name
    python install_command.py --uninstall    remove it again

After installing, do this:
    1. Go to any folder in File Explorer
    2. Click the address bar, type  cmd  (or  powershell)  and press Enter
    3. Type:  start_here
The toolbox opens and "This folder" is already selected.
You can also give it a folder:   start_here "D:\\Inbox"

What it does: puts one tiny launcher file where Windows/your shell already looks for
commands (Windows: %LOCALAPPDATA%\\Microsoft\\WindowsApps - works immediately; fallback:
%LOCALAPPDATA%\\SmartFileOrganizer\\bin added to YOUR user PATH; Mac/Linux: ~/.local/bin).
No admin rights needed. The launcher survives Python being updated, and tells you clearly
if this project folder was moved (just run the installer again).
"""
import sys

if sys.version_info < (3, 8):
    print("This tool needs Python 3.8 or newer (you have {}).".format(sys.version.split()[0]))
    print("Please install a newer Python from https://www.python.org/downloads/")
    sys.exit(1)

import argparse  # noqa: E402
import os        # noqa: E402
import shutil    # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
TOOLBOX = HERE / "toolbox.py"


# --------------------------------------------------------------------------- #
#  The launcher files
# --------------------------------------------------------------------------- #
def _bat_escape(text):
    return text.replace("%", "%%")


def windows_shim(python, toolbox):
    """A launcher that keeps working if Python moves, and explains if the project moved."""
    lines = [
        "@echo off",
        "setlocal",
        'set "SFO_TOOLBOX={}"'.format(_bat_escape(str(toolbox))),
        'set "SFO_PYTHON={}"'.format(_bat_escape(str(python))),
        'if not exist "%SFO_TOOLBOX%" goto moved',
        'if exist "%SFO_PYTHON%" goto runbaked',
        "where py >nul 2>nul",
        "if %errorlevel%==0 goto runpy",
        "where python >nul 2>nul",
        "if %errorlevel%==0 goto runpython",
        "goto nopython",
        ":runbaked",
        '"%SFO_PYTHON%" "%SFO_TOOLBOX%" --here %*',
        "goto :eof",
        ":runpy",
        'py -3 "%SFO_TOOLBOX%" --here %*',
        "goto :eof",
        ":runpython",
        'python "%SFO_TOOLBOX%" --here %*',
        "goto :eof",
        ":moved",
        "echo.",
        "echo  The Smart File Organizer folder was moved or deleted.",
        "echo  Open its new location and double-click INSTALL_COMMAND.bat again.",
        "exit /b 1",
        ":nopython",
        "echo.",
        "echo  Python was not found. Install it from https://www.python.org/downloads/",
        "echo  and tick Add Python to PATH, then try again.",
        "exit /b 1",
    ]
    return "\r\n".join(lines) + "\r\n"


def unix_shim(python, toolbox):
    return ('#!/bin/sh\n'
            'if [ ! -f "{tb}" ]; then\n'
            '  echo "The Smart File Organizer folder was moved or deleted."\n'
            '  echo "Open its new location and run:  python3 python/install_command.py"\n'
            '  exit 1\n'
            'fi\n'
            'if [ -x "{py}" ]; then exec "{py}" "{tb}" --here "$@"; fi\n'
            'exec python3 "{tb}" --here "$@"\n').format(py=python, tb=toolbox)


def _local_app_data():
    return Path(os.environ.get("LOCALAPPDATA") or Path.home())


def windows_bin_dir():
    """Our own private folder (fallback)."""
    return _local_app_data() / "SmartFileOrganizer" / "bin"


def unix_bin_dir():
    return Path.home() / ".local" / "bin"


def _same(a, b):
    return a.rstrip("\\/").lower() == b.rstrip("\\/").lower()


def choose_windows_bin_dir(localappdata=None, path_env=None):
    """Return (folder, needs_path_edit).

    Windows 10/11 already have  %LOCALAPPDATA%\\Microsoft\\WindowsApps  on every user's PATH
    and it is writable. A command placed there works IMMEDIATELY - even in terminals opened
    from File Explorer, which otherwise keep an old copy of PATH until you sign out.
    """
    base = Path(localappdata) if localappdata else _local_app_data()
    path_env = os.environ.get("PATH", "") if path_env is None else path_env
    apps = base / "Microsoft" / "WindowsApps"
    on_path = any(_same(p, str(apps)) for p in path_env.split(os.pathsep) if p)
    if apps.is_dir() and on_path and os.access(str(apps), os.W_OK):
        return apps, False
    return base / "SmartFileOrganizer" / "bin", True


def find_shims(name):
    if os.name == "nt":
        folders, suffix = [_local_app_data() / "Microsoft" / "WindowsApps", windows_bin_dir()], ".cmd"
    else:
        folders, suffix = [unix_bin_dir()], ""
    return [f / (name + suffix) for f in folders if (f / (name + suffix)).exists()]


# --------------------------------------------------------------------------- #
#  Windows: user PATH (registry), no admin needed
# --------------------------------------------------------------------------- #
def _broadcast_environment_change():
    try:
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002,
                                                 5000, None)
    except Exception:
        pass


def registry_path_has(directory):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, "Path")
        return any(_same(p, str(directory)) for p in value.split(";") if p)
    except Exception:
        return False


def edit_user_path(directory, add=True):
    """Add/remove a folder in the user PATH. Returns True if something changed."""
    import winreg
    directory = str(directory)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                        winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
        try:
            value, kind = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            value, kind = "", winreg.REG_EXPAND_SZ
        parts = [p for p in value.split(";") if p]
        present = any(_same(p, directory) for p in parts)
        if add and not present:
            parts.append(directory)
        elif not add and present:
            parts = [p for p in parts if not _same(p, directory)]
        else:
            return False
        if kind not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
            kind = winreg.REG_EXPAND_SZ
        winreg.SetValueEx(key, "Path", 0, kind, ";".join(parts))
    _broadcast_environment_change()
    return True


# --------------------------------------------------------------------------- #
#  Check (doctor)
# --------------------------------------------------------------------------- #
def check(name):
    """Test the command and explain, in plain words, what to do if it won't work."""
    print("Checking the '{}' command ...".format(name))
    print("  Python : {} ({})".format(sys.version.split()[0], sys.executable))
    healthy = True
    if TOOLBOX.exists():
        print("  [ok] Toolbox found: {}".format(TOOLBOX))
    else:
        print("  [x] Toolbox missing: {}".format(TOOLBOX))
        healthy = False
    shims = find_shims(name)
    if not shims:
        print("  [x] The command is not installed yet.")
        print("      Fix: double-click INSTALL_COMMAND.bat (or run: python install_command.py)")
        return 1
    for shim in shims:
        print("  [ok] Launcher file: {}".format(shim))
    found = shutil.which(name)
    if found:
        print("  [ok] This window can run it: {}".format(found))
        print("\nAll good. Type  {}  in any folder.".format(name))
        return 0 if healthy else 1
    folder = shims[0].parent
    print("  [!] This window cannot find '{}' yet.".format(name))
    if os.name == "nt":
        if registry_path_has(folder):
            print("  [ok] The folder is saved in your PATH, so NEW windows will find it.")
        print()
        print("  Why: a window that was open BEFORE the install - or one opened from File")
        print("  Explorer's address bar - keeps an old copy of PATH.")
        print("  Fix (pick one):")
        print("    1. PowerShell, this window only:  $env:Path += ';{}'".format(folder))
        print("       Command Prompt, this window only:  set \"PATH=%PATH%;{}\"".format(folder))
        print("    2. Open a NEW terminal from the Start menu, then use  cd  to reach a folder")
        print("    3. Sign out of Windows and back in once (fixes it everywhere, for good)")
    else:
        print('  Add this line to ~/.bashrc or ~/.zshrc, then open a new terminal:')
        print('      export PATH="{}:$PATH"'.format(folder))
    return 1


# --------------------------------------------------------------------------- #
#  Install / uninstall
# --------------------------------------------------------------------------- #
def install(name):
    if os.name == "nt":
        bindir, needs_path = choose_windows_bin_dir()
        bindir.mkdir(parents=True, exist_ok=True)
        shim = bindir / (name + ".cmd")
        text = windows_shim(sys.executable, TOOLBOX)
        try:
            shim.write_bytes(text.encode("oem"))
        except (LookupError, UnicodeEncodeError):
            shim.write_bytes(text.encode("utf-8"))
        print("[ok] Created {}".format(shim))
        if needs_path:
            edit_user_path(bindir, add=True)
            print("[ok] Added {} to your PATH".format(bindir))
    else:
        bindir = unix_bin_dir()
        bindir.mkdir(parents=True, exist_ok=True)
        shim = bindir / name
        shim.write_text(unix_shim(sys.executable, TOOLBOX))
        shim.chmod(0o755)
        print("[ok] Created {}".format(shim))
    print()
    check(name)                                   # verify, and explain if something is stale
    print()
    print("How to use it:")
    if os.name == "nt":
        print("  1. Open any folder in File Explorer")
        print("  2. Click the address bar, type  cmd  (or  powershell)  and press Enter")
        print("  3. Type:  {}".format(name))
        print("Problems? Double-click CHECK_COMMAND.bat - it tells you exactly what to do.")
    else:
        print("  1. Open a terminal in any folder (cd there)")
        print("  2. Type:  {}".format(name))
        print("Problems? Run:  python3 python/install_command.py --check")
    return 0


def uninstall(name):
    found = False
    for shim in find_shims(name):
        shim.unlink()
        found = True
        print("[ok] Removed {}".format(shim))
    if not found:
        print("The command '{}' was not installed.".format(name))
    if os.name == "nt":
        own = windows_bin_dir()
        try:
            if own.is_dir() and not any(own.iterdir()):
                own.rmdir()
                if not any(own.parent.iterdir()):
                    own.parent.rmdir()
            if not own.exists() and edit_user_path(own, add=False):
                print("[ok] Removed {} from your PATH".format(own))
        except OSError:
            pass
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install a global 'start_here' command.")
    parser.add_argument("--name", default="start_here", help="command name (default start_here)")
    parser.add_argument("--uninstall", action="store_true", help="remove the command")
    parser.add_argument("--check", action="store_true", help="test the command and explain problems")
    args = parser.parse_args(argv)
    if not args.name.replace("_", "").replace("-", "").isalnum():
        print("Please use only letters, numbers, - and _ in the command name.")
        return 2
    if args.uninstall:
        return uninstall(args.name)
    if args.check:
        return check(args.name)
    return install(args.name)


if __name__ == "__main__":
    sys.exit(main())

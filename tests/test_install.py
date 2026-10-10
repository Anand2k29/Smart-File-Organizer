"""Tests for the global 'start_here' command and the 'This folder' shortcut.
Run:  python -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PYDIR = Path(__file__).resolve().parent.parent / "python"
sys.path.insert(0, str(PYDIR))

import install_command   # noqa: E402


class InstallTests(unittest.TestCase):
    def test_windows_shim_is_robust(self):
        text = install_command.windows_shim(r"C:\Python (x86)\python.exe", r"D:\Org 100%\python\toolbox.py")
        self.assertTrue(text.startswith("@echo off"))
        self.assertIn(r'set "SFO_PYTHON=C:\Python (x86)\python.exe"', text)
        self.assertIn(r'set "SFO_TOOLBOX=D:\Org 100%%\python\toolbox.py"', text)   # % is escaped
        self.assertIn('"%SFO_PYTHON%" "%SFO_TOOLBOX%" --here %*', text)             # passes arguments
        self.assertIn('py -3 "%SFO_TOOLBOX%" --here %*', text)                      # Python moved
        self.assertIn("moved or deleted", text)                                     # project moved
        self.assertIn("Python was not found", text)                                 # no Python at all
        self.assertTrue(all(line.endswith("\r") for line in text.split("\n")[:-1]))  # CRLF

    def test_unix_shim(self):
        text = install_command.unix_shim("/usr/bin/python3", "/x/toolbox.py")
        self.assertIn('exec "/usr/bin/python3" "/x/toolbox.py" --here "$@"', text)

    def test_windows_prefers_windowsapps_when_it_is_already_on_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apps = Path(tmp, "Microsoft", "WindowsApps")
            apps.mkdir(parents=True)
            folder, needs_path = install_command.choose_windows_bin_dir(
                tmp, os.pathsep.join(["/x/y", str(apps)]))
            self.assertEqual(folder, apps)
            self.assertFalse(needs_path)

    def test_windows_falls_back_to_own_folder_and_path_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, needs_path = install_command.choose_windows_bin_dir(tmp, "/x/y")
            self.assertEqual(folder, Path(tmp, "SmartFileOrganizer", "bin"))
            self.assertTrue(needs_path)

    def test_unix_shim_mentions_moved_folder(self):
        self.assertIn("moved or deleted", install_command.unix_shim("/p", "/t"))

    @unittest.skipIf(os.name == "nt", "Unix install path")
    def test_check_reports_installed_and_not_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            with mock.patch.dict(os.environ, {"HOME": str(home)}):
                self.assertEqual(install_command.check("nothing_here_xyz"), 1)       # not installed
                install_command.main(["--name", "chk_cmd"])
                bindir = str(home / ".local" / "bin")
                with mock.patch.dict(os.environ, {"PATH": bindir + os.pathsep + os.environ["PATH"]}):
                    self.assertEqual(install_command.main(["--check", "--name", "chk_cmd"]), 0)
                with mock.patch.dict(os.environ, {"PATH": "/usr/bin"}):               # stale PATH
                    self.assertEqual(install_command.main(["--check", "--name", "chk_cmd"]), 1)
                install_command.main(["--name", "chk_cmd", "--uninstall"])

    def test_bad_command_name_is_refused(self):
        self.assertEqual(install_command.main(["--name", "bad name!"]), 2)

    @unittest.skipIf(os.name == "nt", "Unix install path")
    def test_install_run_in_a_folder_and_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, work = Path(tmp, "home"), Path(tmp, "work")
            home.mkdir(); work.mkdir()
            old_home = os.environ.get("HOME")
            os.environ["HOME"] = str(home)
            try:
                self.assertEqual(install_command.main(["--name", "sh_test"]), 0)
                shim = home / ".local" / "bin" / "sh_test"
                self.assertTrue(os.access(shim, os.X_OK))
                # Run the command "inside" the work folder: menu 1 (tidy), Enter = this folder
                (work / "a.pdf").write_text("x")
                os.utime(work / "a.pdf", (1, 1))
                result = subprocess.run([str(shim)], input="1\n\n2\n\n0\n", cwd=str(work),
                                        capture_output=True, text=True,
                                        env=dict(os.environ, HOME=str(home)))
                self.assertIn("Working in: " + str(work.resolve()), result.stdout)
                self.assertIn("This folder", result.stdout)
                self.assertIn("Documents/", result.stdout)             # the preview was shown
                self.assertTrue((work / "a.pdf").exists())            # cancelled -> unchanged
                self.assertEqual(install_command.main(["--name", "sh_test", "--uninstall"]), 0)
                self.assertFalse(shim.exists())
            finally:
                if old_home is None:
                    os.environ.pop("HOME", None)
                else:
                    os.environ["HOME"] = old_home


if __name__ == "__main__":
    unittest.main()

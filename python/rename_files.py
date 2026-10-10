#!/usr/bin/env python3
"""
rename_files.py - rename many files at once, with a preview and UNDO.

    python rename_files.py FOLDER --lower                  Photo.JPG      -> photo.jpg
    python rename_files.py FOLDER --spaces                 my file.txt    -> my_file.txt
    python rename_files.py FOLDER --clean                  a#b&c%.pdf     -> abc.pdf
    python rename_files.py FOLDER --date-prefix            scan.pdf       -> 2026-10-09_scan.pdf
    python rename_files.py FOLDER --number trip            IMG_8.jpg      -> trip_001.jpg
    python rename_files.py FOLDER --prefix "Invoice_"      a.pdf          -> Invoice_a.pdf
    python rename_files.py FOLDER --suffix "_final"        a.pdf          -> a_final.pdf
    python rename_files.py FOLDER --replace "IMG" "Holiday"
    python rename_files.py FOLDER --lower --spaces --only "*.jpg"      (combine them)

Only loose files are renamed (not sub-folders). Nothing is overwritten.
Undo with:  python smart_organizer.py FOLDER --undo
"""
import argparse
import fnmatch
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common        # noqa: E402
from ui import UI    # noqa: E402


def new_name(path, args, index):
    stem, ext = path.stem, path.suffix
    if args.replace:
        stem = stem.replace(args.replace[0], args.replace[1])
    if args.clean:
        stem = re.sub(r"[^\w\s\-\.\(\)]", "", stem)
        stem = re.sub(r"\s{2,}", " ", stem).strip()
    if args.spaces:
        stem = re.sub(r"\s+", "_", stem)
    if args.number:
        stem = "{}_{:03d}".format(args.number, index)
    if args.lower:
        stem, ext = stem.lower(), ext.lower()
    if args.prefix:
        stem = args.prefix + stem
    if args.suffix:
        stem = stem + args.suffix
    if args.date_prefix:
        when = datetime.fromtimestamp(path.stat().st_mtime)
        stem = "{:%Y-%m-%d}_{}".format(when, stem)
    return (stem or path.stem) + ext


def build_plan(folder, args):
    """[(source, destination)] for every file whose name would change."""
    folder = Path(folder)
    files = [p for p in sorted(folder.iterdir(), key=lambda p: p.name.lower())
             if p.is_file() and not common.is_hidden(p)
             and (not args.only or fnmatch.fnmatch(p.name.lower(), args.only.lower()))]
    existing = {p.name.lower() for p in folder.iterdir()}
    used, plan = set(), []
    for index, src in enumerate(files, 1):
        name = new_name(src, args, index)
        if name == src.name:
            continue
        case_only = name.lower() == src.name.lower()
        candidate, n = Path(name), 1
        while not case_only and (candidate.name.lower() in existing
                                 or candidate.name.lower() in used):
            candidate = Path("{} ({}){}".format(Path(name).stem, n, Path(name).suffix))
            n += 1
        used.add(candidate.name.lower())
        plan.append((src, folder / candidate.name))
    return plan


def apply_rename(src, dest):
    if src.name.lower() == dest.name.lower():            # only the capitals change
        temp = src.with_name(src.name + ".__renaming__")
        src.rename(temp)
        temp.rename(dest)
    else:
        src.rename(dest)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rename many files at once (with undo).")
    parser.add_argument("folder")
    parser.add_argument("--lower", action="store_true", help="make names lowercase")
    parser.add_argument("--spaces", action="store_true", help="spaces -> underscores")
    parser.add_argument("--clean", action="store_true", help="remove odd characters")
    parser.add_argument("--date-prefix", action="store_true",
                        help="add the file's date to the start (2026-10-09_name)")
    parser.add_argument("--number", metavar="NAME", help="rename to NAME_001, NAME_002 ...")
    parser.add_argument("--prefix", metavar="TEXT", help="add text at the start")
    parser.add_argument("--suffix", metavar="TEXT", help="add text at the end (before .ext)")
    parser.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"), help="replace text")
    parser.add_argument("--only", metavar="PATTERN", help='only files like "*.jpg"')
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    args = parser.parse_args(argv)

    ui = UI()
    folder = common.clean_path(args.folder)
    problem = common.check_folder(folder)
    if problem:
        ui.error(problem)
        return 2
    folder = folder.resolve()
    if not any([args.lower, args.spaces, args.clean, args.date_prefix, args.number,
                args.prefix, args.suffix, args.replace]):
        ui.error("Choose at least one change, e.g. --lower or --spaces  (see --help).")
        return 2

    plan = build_plan(folder, args)
    if not plan:
        ui.ok("No names would change. Nothing to do.")
        return 0
    ui.heading("Preview: {} file(s) would be renamed".format(len(plan)))
    for src, dest in plan[:30]:
        ui.say("  {}  ->  {}".format(src.name, ui.c(dest.name, "green")))
    if len(plan) > 30:
        ui.say("  ... and {} more".format(len(plan) - 30))
    if args.dry_run:
        ui.info("Dry run - nothing was renamed.")
        return 0
    if not args.yes and not common.confirm("\nRename these {} file(s)?".format(len(plan))):
        ui.ok("Cancelled. Nothing was renamed.")
        return 0

    moves = []
    for i, (src, dest) in enumerate(plan, 1):
        common.tick(ui, i - 1, len(plan), src.name)
        try:
            apply_rename(src, dest)
            moves.append({"from": str(src), "to": str(dest)})
        except OSError as err:
            ui.warn("Could not rename {}: {}".format(src.name, err))
    common.tick(ui, len(plan), len(plan), "done")
    ui.end_progress()
    if moves:
        common.write_log(folder, "rename", moves)
    ui.celebrate("Renamed {} file(s)".format(len(moves)))
    ui.info("Undo anytime from the toolbox, or:  python smart_organizer.py \"{}\" --undo".format(folder))
    return 0


if __name__ == "__main__":
    sys.exit(main())

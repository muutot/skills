"""
Export SKILL.md files to opencode / claude / codex directory structures.

Scans this repository for */SKILL.md definitions (flat and nested),
reads the `name` field from YAML frontmatter, and copies each skill
into the target tool's expected `<tool>/skills/<name>/SKILL.md` layout.

Targets:
  opencode  ->  .opencode/skills/<name>/SKILL.md
  claude    ->  .claude/skills/<name>/SKILL.md
  codex     ->  .agents/skills/<name>/SKILL.md

Export script
python skills/skill-export.py                           # export to all three tools
python skills/skill-export.py -t claude codex           # export to specific tools
python skills/skill-export.py -t opencode -m symlink    # use symbolic links
python skills/skill-export.py -f                        # overwrite existing files

Options:

Flag	                Default	        Description
-t / --target	        all three	    Tools: opencode, claude, codex
-o / --output-dir	    .	            Output root directory
-s / --source-dir	    .	            Scan directory for SKILL.md files
-m / --mode	            copy	        copy, symlink, or hardlink
-f / --force	        —	            Overwrite existing files
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


TOOL_DIRS = {
    "opencode": ".opencode/skills",
    "claude": ".claude/skills",
    "codex": ".agents/skills",
}


EXCLUDE_DIRS = {".git", ".opencode", ".claude", ".agents", ".idea", "node_modules"}
VALID_SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def is_valid_skill_name(name: str) -> bool:
    """Return True when name is safe to use as a single path segment."""
    return bool(VALID_SKILL_NAME_RE.fullmatch(name))


def parse_frontmatter(path: Path) -> dict | None:
    """Extract name and description from YAML frontmatter in SKILL.md."""
    content = path.read_text(encoding="utf-8")
    m = re.search(r"^---\s*$(.+?)^---\s*$", content, re.MULTILINE | re.DOTALL)
    if not m:
        print(f"  [!] no frontmatter found: {path}")
        return None
    yaml_block = m.group(1)

    name_match = re.search(r"^name:\s*(.+?)$", yaml_block, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+?)$", yaml_block, re.MULTILINE)

    name = name_match.group(1).strip() if name_match else ""
    desc = desc_match.group(1).strip() if desc_match else ""

    # unfold YAML block scalar (>)
    if desc == ">":
        lines = yaml_block.splitlines()
        in_block = False
        block_lines = []
        for line in lines:
            if re.match(r"^description:\s*>\s*$", line):
                in_block = True
                continue
            if in_block:
                if re.match(r"^\S", line) or (not line.strip() and block_lines):
                    break
                if re.match(r"^\s+\S", line):
                    block_lines.append(line.rstrip())
        if block_lines:
            desc = " ".join(block_lines).strip()

    if not name:
        print(f"  [!] missing 'name' in frontmatter: {path}")
        return None

    if not is_valid_skill_name(name):
        print(f"  [!] invalid 'name' in frontmatter: {path} ({name!r})")
        return None

    return {"name": name, "description": desc}


def copy_file(src: Path, dst: Path, mode: str, force: bool) -> None:
    """Copy / symlink / hardlink src -> dst."""
    dst.parent.mkdir(parents=True, exist_ok=True)

    dst_present = dst.exists() or dst.is_symlink()

    if dst_present and not force:
        print(f"  [!] exists: {dst} (use --force)")
        return

    if dst_present:
        dst.unlink()

    if mode == "copy":
        shutil.copy2(src, dst)
        print(f"  [copy] {dst}")
    elif mode == "symlink":
        os.symlink(src.resolve(), dst)
        print(f"  [symlink] {dst}")
    elif mode == "hardlink":
        os.link(src.resolve(), dst)
        print(f"  [hardlink] {dst}")


def discover_skills(source_dir: Path) -> list[dict]:
    """Find all SKILL.md files not in excluded dirs."""
    skills = []
    for fpath in source_dir.rglob("SKILL.md"):
        # skip excluded dirs
        parts = fpath.relative_to(source_dir).parts
        if any(p in EXCLUDE_DIRS for p in parts):
            continue

        meta = parse_frontmatter(fpath)
        if meta is None:
            continue

        meta["source_path"] = fpath
        skills.append(meta)
        preview = meta["description"][:60]
        print(f"  - {meta['name']}: {preview}...")

    return skills


def main():
    parser = argparse.ArgumentParser(description="Export skills to opencode / claude / codex")
    parser.add_argument(
        "--target",
        "-t",
        nargs="+",
        choices=["opencode", "claude", "codex"],
        default=["opencode", "claude", "codex"],
        help="Target tool(s) to export to (default: all three)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path.cwd(),
        help="Output root directory (default: current dir)",
    )
    parser.add_argument(
        "--source-dir",
        "-s",
        type=Path,
        default=Path.cwd(),
        help="Where to scan for */SKILL.md files (default: current dir)",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["copy", "symlink", "hardlink"],
        default="copy",
        help="File operation mode (default: copy)",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite existing files",
    )
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()

    print(f"Scanning {source_dir} ...")
    skills = discover_skills(source_dir)

    if not skills:
        print("No SKILL.md files found.")
        sys.exit(0)

    print(f"\nDiscovered {len(skills)} skill(s).\n")

    for tool in args.target:
        base = (output_dir / TOOL_DIRS[tool]).resolve()
        print(f"── {tool} -> {base}")

        for s in skills:
            dst = (base / s["name"] / "SKILL.md").resolve()
            if not dst.is_relative_to(base):
                print(f"  [!] refusing to write outside {base}: {dst}")
                continue
            copy_file(s["source_path"], dst, args.mode, args.force)
        print()

    print("Done.")


if __name__ == "__main__":
    main()

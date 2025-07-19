#!/usr/bin/env python3
"""release.py

Release helper script for GraphMyTunes.

This script helps manage releases by:
1. Updating version in pyproject.toml
2. Creating and pushing appropriate git tags
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from packaging.version import Version


def build_argument_parser():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "version",
        help="New version number (e.g., 1.0.0, 1.0.0a1)",
    )
    parser.add_argument(
        "--tag-only",
        action="store_true",
        help="Only create tag, don't update version in pyproject.toml",
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Only update version, don't create tag",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    return parser


def get_current_version():
    """Read current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def validate_version_sequence(current_version, new_version):
    """Validate that new version is greater than current version."""
    try:
        current = Version(current_version)
        new = Version(new_version)
        if new <= current:
            print(
                f"Error: New version {new_version} is not greater than current version {current_version}"
            )
            return False
        return True
    except (ValueError, TypeError) as e:
        print(f"Error parsing versions: {e}")
        return False


def check_changelog_updated(new_version):
    """Check if changelog has been updated with the new version."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("Warning: CHANGELOG.md not found")
        return True  # Don't block release if no changelog

    content = changelog_path.read_text(encoding="utf-8")
    # Look for version header like "## [1.2.3] - 2024-01-01"
    version_pattern = rf"##\s*\[{re.escape(new_version)}\]"
    if not re.search(version_pattern, content):
        print(
            f"Warning: Could not find entry for version {new_version} in CHANGELOG.md"
        )
        response = input("Continue anyway? (y/N): ")
        return response.lower() == "y"
    return True


def update_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")

    # Replace version
    updated_content = re.sub(
        r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', content
    )

    pyproject_path.write_text(updated_content, encoding="utf-8")
    print(f"Updated version to {new_version} in pyproject.toml")


def create_tag(version_num):
    """Create and push git tag."""
    # Ensure we're on main branch
    try:
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip()
        if current_branch != "main":
            print(
                f"Error: Currently on branch '{current_branch}', but releases should be made from 'main'"
            )
            print("Please merge changes to main branch and try again.")
            return False
    except subprocess.CalledProcessError:
        print("Error: Could not determine current git branch")
        return False

    # Check for uncommitted changes
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            print("Error: You have uncommitted changes:")
            print(result.stdout)
            print("Please commit or stash changes before creating a tag.")
            return False
    except subprocess.CalledProcessError:
        print("Error: Could not check git status")
        return False

    tag_name = f"v{version_num}"

    try:
        # Create tag
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"Release {version_num}"], check=True
        )
        print(f"Created tag {tag_name}")

        # Push tag
        subprocess.run(["git", "push", "origin", tag_name], check=True)
        print(f"Pushed tag {tag_name} to origin")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error creating or pushing tag: {e}")
        return False


def main():
    """Main process."""

    # Parse command line arguments.
    argparser = build_argument_parser()
    args = argparser.parse_args()

    current_version = get_current_version()
    print(f"Current version: {current_version}")
    print(f"New version: {args.version}")

    # Validate version format
    version_pattern = r"^\d+\.\d+\.\d+(?:[ab]\d+|rc\d+)?$"
    if not re.match(version_pattern, args.version):
        print(
            "Error: Invalid version format. Use format like 1.0.0, 1.0.0a1, 1.0.0b1, or 1.0.0rc1"
        )
        sys.exit(1)

    # Validate version sequence
    if not validate_version_sequence(current_version, args.version):
        sys.exit(1)

    # Check changelog
    if not check_changelog_updated(args.version):
        sys.exit(1)

    if args.dry_run:
        print("\n--- DRY RUN MODE ---")
        if not args.tag_only:
            print(f"Would update version in pyproject.toml to {args.version}")
        if not args.no_tag:
            print(f"Would create and push git tag v{args.version}")
        print("--- END DRY RUN ---")
        return

    # Update version if not tag-only
    if not args.tag_only:
        update_version(args.version)
        print("Don't forget to commit the version change!")

        if not args.no_tag:
            response = input("Commit changes now? (y/N): ")
            if response.lower() == "y":
                try:
                    subprocess.run(["git", "add", "pyproject.toml"], check=True)
                    subprocess.run(
                        ["git", "commit", "-m", f"Bump version to {args.version}"],
                        check=True,
                    )
                    subprocess.run(["git", "push"], check=True)
                    print("Committed and pushed version change")
                except subprocess.CalledProcessError:
                    print("Error committing changes")
                    return

    # Create tag if not no-tag
    if not args.no_tag:
        if create_tag(args.version):
            # Determine what happens next based on version type
            is_prerelease = any(x in args.version for x in ["a", "b", "rc"])

            if is_prerelease:
                print(f"\n🚀 Pre-release tag v{args.version} created and pushed!")
            else:
                print(f"\n🎉 Final release tag v{args.version} created and pushed!")

            print("\nFor next steps, see:")
            print("https://github.com/homebysix/GraphMyTunes/blob/main/RELEASING.md")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""release.py

Release helper script for GraphMyTunes.

This script helps manage releases by:
1. Updating version in pyproject.toml
2. Creating appropriate git tags
3. Providing next steps for publishing
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Read current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def update_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Replace version
    updated_content = re.sub(
        r'version\s*=\s*"[^"]+"', f'version = "{new_version}"', content
    )

    pyproject_path.write_text(updated_content)
    print(f"Updated version to {new_version} in pyproject.toml")


def create_tag(version, tag_type="release"):
    """Create and push git tag."""
    # Ensure we're on main branch
    try:
        current_branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip()
        if current_branch != "main":
            print(f"Warning: Currently on branch '{current_branch}', not 'main'")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != "y":
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

    tag_name = f"v{version}"

    try:
        # Create tag
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"Release {version}"], check=True
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
    parser = argparse.ArgumentParser(description="Release helper for GraphMyTunes")
    parser.add_argument("version", help="New version number (e.g., 1.0.0, 1.0.0a1)")
    parser.add_argument(
        "--tag-only",
        action="store_true",
        help="Only create tag, don't update version in pyproject.toml",
    )
    parser.add_argument(
        "--no-tag", action="store_true", help="Only update version, don't create tag"
    )

    args = parser.parse_args()

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
            # Determine publishing destination
            if any(x in args.version for x in ["a", "b", "rc"]):
                print(f"\n✅ Pre-release tag v{args.version} created!")
                print("📦 This will automatically publish to TestPyPI")
                print("🔗 Check: https://test.pypi.org/project/GraphMyTunes/")
            else:
                print(f"\n✅ Release tag v{args.version} created!")
                print("📦 This will automatically publish to PyPI")
                print("🔗 Check: https://pypi.org/project/GraphMyTunes/")

            print(
                "\n🚀 View workflow: https://github.com/homebysix/GraphMyTunes/actions"
            )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create git worktrees with isolated Python environments.

This script automates the creation of git worktrees with per-worktree Python
virtual environments, enabling parallel development on multiple branches without
environment conflicts or lock contention.

Usage:
    create_worktree.py <worktree-name> <branch-name> [OPTIONS]

Positional Arguments:
    worktree-name       Name of the worktree directory (e.g., feature-x)
    branch-name         Name of the git branch (e.g., feature-x-implementation)

Options:
    --source-branch SOURCE
        Branch to create the new branch from (default: main)
        Supports local branches (e.g., feature-xyz) and remote branches
        (e.g., origin/feature-xyz)

    --include-changes {none,uncommitted,unpushed,all}
        Include changes from source worktree (non-interactive mode)
        - none: Branch from last pushed commit (excludes all local work)
        - uncommitted: Include uncommitted changes only
        - unpushed: Include unpushed commits only
        - all: Include both uncommitted changes and unpushed commits

    --exclude-changes
        Exclude all changes from source worktree (same as --include-changes=none)

Interactive Mode:
    When the source branch is checked out in a worktree with uncommitted changes
    or unpushed commits, the script prompts you to choose what to include.
    This prompt is skipped if --include-changes or --exclude-changes is specified.

Examples:
    # Basic usage (branches from main)
    create_worktree.py feature-x feature-x-implementation

    # Branch from feature branch
    create_worktree.py fix-docs fix-docs-typos --source-branch feature-validation

    # Branch from remote branch
    create_worktree.py hotfix hotfix-critical --source-branch origin/release-1.0

    # Include all changes from source worktree (non-interactive)
    create_worktree.py parallel parallel-dev --source-branch feature-x \\
        --include-changes=all

    # Exclude all local changes (non-interactive)
    create_worktree.py clean clean-branch --source-branch feature-x --exclude-changes

What This Script Does:
    1. Validates source branch exists (local or remote)
    2. Finds worktree containing source branch (if any)
    3. Detects uncommitted changes and unpushed commits
    4. Prompts to include changes (unless flags specify behavior)
    5. Creates new worktree as sibling directory (e.g., ../feature-x/)
    6. Creates isolated Python virtual environment using uv
    7. Installs project dependencies into the worktree's venv

Architecture:
    Worktrees are created as sibling directories to the main repository:

    project/
    ├── main/           # Main worktree
    ├── feature-x/      # Feature worktree
    └── hotfix/         # Hotfix worktree

    Each worktree has its own .venv/ with isolated dependencies, preventing
    lock contention when running tools like pytest, ruff, or mypy in parallel.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import NoReturn


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


def print_error(message: str) -> None:
    """Print error message in red to stderr."""
    print(f"{Colors.RED}Error: {message}{Colors.NC}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print informational message in blue."""
    print(f"{Colors.BLUE}{message}{Colors.NC}")


def print_success(message: str) -> None:
    """Print success message in green."""
    print(f"{Colors.GREEN}{message}{Colors.NC}")


def print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}{message}{Colors.NC}")


def exit_with_error(message: str) -> NoReturn:
    """Print error message and exit with status 1."""
    print_error(message)
    sys.exit(1)


def run_git(
    *args: str, cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run git command and return result.

    Args:
        *args: Git command arguments (e.g., 'status', '--porcelain')
        cwd: Working directory for git command
        check: If True, raise CalledProcessError on non-zero exit

    Returns:
        CompletedProcess with stdout, stderr, and returncode

    Raises:
        SystemExit: If check=True and git command fails
    """
    try:
        return subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        exit_with_error(f"Git command failed: {e.stderr.strip()}")


def check_uv_available() -> None:
    """Check if uv is installed and available.

    Raises:
        SystemExit: If uv is not found
    """
    try:
        subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
    except FileNotFoundError:
        exit_with_error(
            "uv is not installed\n"
            "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "Or visit: https://docs.astral.sh/uv/getting-started/installation/"
        )
    except subprocess.TimeoutExpired:
        exit_with_error("uv check timed out - this may indicate a system issue")


def validate_project_repo() -> None:
    """Validate we're in a git repository with pyproject.toml.

    Raises:
        SystemExit: If not in a git repository or pyproject.toml missing
    """
    if not Path(".git").is_dir() and not Path(".git").is_file():
        exit_with_error(
            "Not in a git repository\n"
            "Please run this script from the repository root directory"
        )

    if not Path("pyproject.toml").exists():
        print_warning("Warning: pyproject.toml not found in current directory")
        print("This script expects a Python project with pyproject.toml")
        response = input("Continue anyway? (y/N) ").strip().lower()
        if response not in ("y", "yes"):
            sys.exit(1)


def validate_source_branch(branch_name: str) -> tuple[bool, str]:
    """Validate that the source branch exists (local or remote).

    Args:
        branch_name: Name of the branch to validate
                    (e.g., 'main', 'feature-xyz', 'origin/feature-xyz')

    Returns:
        Tuple of (is_valid, branch_type) where branch_type is:
        - 'local': Local branch exists
        - 'remote': Remote branch exists
        - '': Branch does not exist
    """
    # Check if it's a local branch
    result = run_git(
        "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}", check=False
    )
    if result.returncode == 0:
        return (True, "local")

    # Check if it's a remote branch
    result = run_git(
        "show-ref", "--verify", "--quiet", f"refs/remotes/{branch_name}", check=False
    )
    if result.returncode == 0:
        return (True, "remote")

    return (False, "")


def find_worktree_for_branch(branch_name: str) -> Path | None:
    """Find the worktree path that has the specified branch checked out.

    Args:
        branch_name: Name of the branch to find (e.g., 'main', 'feature-x')

    Returns:
        Path to worktree if found, None if branch not checked out in any worktree
    """
    result = run_git("worktree", "list", "--porcelain", check=False)
    if result.returncode != 0:
        return None

    current_worktree = None
    current_branch = None

    for line in result.stdout.strip().split("\n"):
        if line.startswith("worktree "):
            current_worktree = Path(line.split(" ", 1)[1])
        elif line.startswith("branch "):
            # Extract branch name from refs/heads/<branch>
            current_branch = (
                line.split("refs/heads/", 1)[1] if "refs/heads/" in line else None
            )
        elif line == "":
            # End of worktree entry
            if current_branch == branch_name and current_worktree:
                return current_worktree
            current_worktree = None
            current_branch = None

    # Check last entry
    if current_branch == branch_name and current_worktree:
        return current_worktree

    return None


def check_local_changes(worktree_path: Path) -> dict[str, bool | int | str]:
    """Check for uncommitted and unpushed changes in specified worktree.

    Args:
        worktree_path: Path to the worktree to check

    Returns:
        Dictionary containing:
            - uncommitted (bool): Has uncommitted changes
            - uncommitted_output (str): Git status output
            - unpushed (bool): Has unpushed commits
            - unpushed_count (int): Number of unpushed commits
            - unpushed_log (str): Formatted log of unpushed commits
    """
    changes: dict[str, bool | int | str] = {
        "uncommitted": False,
        "uncommitted_output": "",
        "unpushed": False,
        "unpushed_count": 0,
        "unpushed_log": "",
    }

    # Check for uncommitted changes
    status_result = run_git("status", "--porcelain", cwd=worktree_path, check=False)
    if status_result.returncode == 0 and status_result.stdout.strip():
        changes["uncommitted"] = True
        changes["uncommitted_output"] = status_result.stdout

    # Check for unpushed commits (requires upstream branch)
    upstream_result = run_git(
        "rev-parse", "--abbrev-ref", "@{u}", cwd=worktree_path, check=False
    )
    if upstream_result.returncode == 0:
        # Count unpushed commits
        count_result = run_git(
            "rev-list", "--count", "@{u}..HEAD", cwd=worktree_path, check=False
        )
        if count_result.returncode == 0:
            count = int(count_result.stdout.strip())
            if count > 0:
                changes["unpushed"] = True
                changes["unpushed_count"] = count

                # Get formatted log of unpushed commits
                log_result = run_git(
                    "log",
                    "@{u}..HEAD",
                    "--oneline",
                    "--no-decorate",
                    cwd=worktree_path,
                    check=False,
                )
                if log_result.returncode == 0:
                    changes["unpushed_log"] = log_result.stdout.strip()

    return changes


def prompt_include_changes(
    branch_name: str, worktree_path: Path, changes_info: dict[str, bool | int | str]
) -> str:
    """Prompt user about including changes from source worktree.

    Args:
        branch_name: Name of the source branch
        worktree_path: Path to the source worktree
        changes_info: Dictionary from check_local_changes()

    Returns:
        User's choice: 'none' | 'uncommitted' | 'unpushed' | 'all'
    """
    print()
    print_info(f"Changes detected in source worktree: {worktree_path}")
    print()

    # Show uncommitted changes
    if changes_info["uncommitted"]:
        print_warning("Uncommitted changes:")
        uncommitted_output = str(changes_info["uncommitted_output"])
        lines = uncommitted_output.strip().split("\n")
        for line in lines[:10]:
            print(f"  {line}")
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more files")
        print()

    # Show unpushed commits
    if changes_info["unpushed"]:
        unpushed_count = int(changes_info["unpushed_count"])
        print_warning(f"Unpushed commits ({unpushed_count}):")
        unpushed_log = str(changes_info["unpushed_log"])
        for line in unpushed_log.split("\n")[:5]:
            print(f"  {line}")
        if unpushed_count > 5:
            print(f"  ... and {unpushed_count - 5} more commits")
        print()

    # Build menu options based on what changes exist
    print("Include changes in new worktree?")
    options: dict[str, str] = {}
    option_num = 1

    # Always offer "none"
    options[str(option_num)] = "none"
    print(f"  {option_num}. None (branch from last pushed commit)")
    option_num += 1

    # Offer uncommitted if they exist
    if changes_info["uncommitted"]:
        options[str(option_num)] = "uncommitted"
        print(f"  {option_num}. Uncommitted only")
        option_num += 1

    # Offer unpushed if they exist
    if changes_info["unpushed"]:
        options[str(option_num)] = "unpushed"
        print(f"  {option_num}. Unpushed commits only")
        option_num += 1

    # Offer "all" if both exist
    if changes_info["uncommitted"] and changes_info["unpushed"]:
        options[str(option_num)] = "all"
        print(f"  {option_num}. All changes (uncommitted + unpushed)")
        default_choice = str(option_num)
    elif changes_info["uncommitted"]:
        default_choice = "2"  # Uncommitted only
    elif changes_info["unpushed"]:
        default_choice = "2"  # Unpushed only
    else:
        default_choice = "1"  # None

    print()

    # Get user choice
    while True:
        choice = input(f"Choice [default: {default_choice}]: ").strip()

        if choice == "":
            return options[default_choice]

        if choice in options:
            return options[choice]

        print(f"Please enter a number between 1 and {len(options)}")


def setup_python_venv(worktree_path: Path) -> None:
    """Create per-worktree Python virtual environment using uv.

    Uses 'uv venv' to create an isolated .venv directory and 'uv sync' to
    install dependencies from the project's uv.lock file. This approach provides
    complete isolation - each worktree has its own Python environment, preventing
    lock contention and conflicts when running tools in parallel.

    Args:
        worktree_path: Path to the newly created worktree

    Raises:
        RuntimeError: If uv is not found or venv creation fails
    """
    print_info("Setting up isolated Python environment...")

    # Read Python version from .python-version file
    python_version_file = worktree_path / ".python-version"
    python_version = None
    if python_version_file.exists():
        try:
            python_version = python_version_file.read_text().strip()
        except Exception:
            pass

    if not python_version:
        python_version = "3.14"  # Default fallback

    # Ensure uv has the requested Python version installed
    print_info(f"Ensuring Python {python_version} is available via uv...")
    try:
        subprocess.run(
            ["uv", "python", "install", python_version],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "uv not found. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"Python {python_version} download timed out. Check network connection."
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "unknown error"
        raise RuntimeError(
            f"Failed to install Python {python_version} via uv: {error_msg}"
        )

    # Create venv using uv's managed Python
    print_info("Creating per-worktree virtual environment...")
    try:
        subprocess.run(
            ["uv", "venv", "--python", python_version],
            cwd=worktree_path,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Verify Python version
        venv_python = worktree_path / ".venv" / "bin" / "python"
        version_result = subprocess.run(
            [str(venv_python), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        actual_version = version_result.stdout.strip()
        print_success(f"  Created venv with {actual_version}")
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Virtual environment creation timed out. This may indicate a uv issue."
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "unknown error"
        raise RuntimeError(f"Failed to create virtual environment with uv: {error_msg}")

    # Install dependencies using uv sync
    print_info("Installing Python dependencies...")

    try:
        subprocess.run(
            ["uv", "sync", "--no-install-project", "--group", "dev"],
            cwd=worktree_path,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        print_success("  Dependencies installed successfully")
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Dependency installation timed out. Check network connection."
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "unknown error"
        raise RuntimeError(f"Failed to install dependencies: {error_msg}")


def main() -> int:
    """Main entry point for worktree creation script."""
    parser = argparse.ArgumentParser(
        description="Create a new git worktree with isolated Python environment",
        epilog="Examples:\n"
        "  create_worktree.py feature-x feature-x-implementation\n"
        "  create_worktree.py fix-docs fix-typos "
        "--source-branch feature-validation\n"
        "  create_worktree.py hotfix hotfix-critical "
        "--source-branch origin/release-1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "worktree_name", help="Name of the worktree directory (e.g., feature-x)"
    )
    parser.add_argument(
        "branch_name", help="Name of the git branch (e.g., feature-x-implementation)"
    )
    parser.add_argument(
        "--source-branch",
        default="main",
        help="Branch to create the new branch from (default: main). "
        "Supports local and remote branches "
        "(e.g., feature-xyz or origin/feature-xyz)",
    )
    parser.add_argument(
        "--include-changes",
        choices=["none", "uncommitted", "unpushed", "all"],
        help="Include changes from source worktree (non-interactive). "
        "Options: none, uncommitted, unpushed, all",
    )
    parser.add_argument(
        "--exclude-changes",
        action="store_true",
        help="Exclude all changes from source worktree "
        "(same as --include-changes=none)",
    )

    args = parser.parse_args()

    # Check that uv is available
    check_uv_available()

    # Validate conflicting flags
    if args.exclude_changes and args.include_changes:
        exit_with_error(
            "Cannot specify both --exclude-changes and --include-changes"
        )

    # Resolve include_changes value
    if args.exclude_changes:
        include_changes_choice: str | None = "none"
    elif args.include_changes:
        include_changes_choice = args.include_changes
    else:
        include_changes_choice = None  # Will prompt if needed

    # Validate we're in a git repository with pyproject.toml
    validate_project_repo()

    # Validate source branch exists
    print_info(f"Validating source branch '{args.source_branch}'...")
    is_valid, branch_type = validate_source_branch(args.source_branch)
    if not is_valid:
        exit_with_error(
            f"Source branch '{args.source_branch}' does not exist\n"
            f"Use 'git branch -a' to see available branches"
        )

    # Find worktree for source branch (if it's checked out somewhere)
    source_worktree_path = None
    if branch_type == "local":
        source_worktree_path = find_worktree_for_branch(args.source_branch)

    # Check for changes in source worktree
    changes_info = None
    if source_worktree_path:
        print_info(
            f"Found worktree for '{args.source_branch}': {source_worktree_path}"
        )
        changes_info = check_local_changes(source_worktree_path)

        # Determine what changes to include
        if changes_info["uncommitted"] or changes_info["unpushed"]:
            # Changes exist - determine what to include
            if include_changes_choice is None:
                # No flags specified - prompt user interactively
                include_changes_choice = prompt_include_changes(
                    args.source_branch, source_worktree_path, changes_info
                )
            else:
                # Flags specified - use non-interactive mode
                print_info(
                    f"Using --include-changes={include_changes_choice} "
                    "(non-interactive)"
                )
        else:
            # No changes exist
            include_changes_choice = "none"
    else:
        # Source branch not in a worktree - must fetch/pull it
        include_changes_choice = "none"

        if branch_type == "local":
            print_info(
                f"Source branch '{args.source_branch}' not checked out in any worktree"
            )
            print_info("Checking out and pulling...")
            run_git("checkout", args.source_branch)
            run_git("pull")
        elif branch_type == "remote":
            print_info(f"Fetching remote branch '{args.source_branch}'...")
            run_git("fetch")

    # Determine worktree path (sibling directory)
    # If we're in /path/to/project/main, create /path/to/project/feature-x
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    worktree_path = parent_dir / args.worktree_name

    # Check if worktree already exists
    if worktree_path.exists():
        exit_with_error(f"Worktree already exists at {worktree_path}")

    # Check if branch already exists
    result = run_git(
        "show-ref", "--verify", "--quiet", f"refs/heads/{args.branch_name}", check=False
    )
    if result.returncode == 0:
        exit_with_error(
            f"Branch '{args.branch_name}' already exists\n"
            f"Use a different branch name or delete the existing branch first"
        )

    # Create the worktree from source branch
    print_info(f"Creating worktree: {worktree_path}")
    print_info(f"  Branching from: {args.source_branch}")

    # Handle different include_changes scenarios
    if include_changes_choice == "none":
        # Branch from remote tracking branch if possible, otherwise from source branch
        if source_worktree_path and changes_info and changes_info["unpushed"]:
            # Get remote tracking branch
            upstream_result = run_git(
                "rev-parse",
                "--abbrev-ref",
                "@{u}",
                cwd=source_worktree_path,
                check=False,
            )
            if upstream_result.returncode == 0:
                upstream_branch = upstream_result.stdout.strip()
                print_info(
                    f"  Excluding unpushed commits "
                    f"(branching from {upstream_branch})"
                )
                run_git(
                    "worktree",
                    "add",
                    str(worktree_path),
                    "-b",
                    args.branch_name,
                    upstream_branch,
                )
            else:
                # No upstream, just use source branch
                run_git(
                    "worktree",
                    "add",
                    str(worktree_path),
                    "-b",
                    args.branch_name,
                    args.source_branch,
                )
        else:
            # Standard case: branch from committed state
            run_git(
                "worktree",
                "add",
                str(worktree_path),
                "-b",
                args.branch_name,
                args.source_branch,
            )

    elif include_changes_choice == "unpushed":
        # Branch from HEAD of source worktree
        # (includes unpushed commits, excludes uncommitted)
        print_info("  Including: unpushed commits only")
        run_git("branch", args.branch_name, cwd=source_worktree_path)
        run_git("worktree", "add", str(worktree_path), args.branch_name)

    elif include_changes_choice in ("uncommitted", "all"):
        # Branch from HEAD + working directory (includes everything)
        print_info(f"  Including: {include_changes_choice} changes")

        # First stash any uncommitted changes in source worktree
        stash_result = run_git(
            "stash",
            "push",
            "-m",
            f"temp-for-{args.branch_name}",
            cwd=source_worktree_path,
            check=False,
        )
        stashed = (
            stash_result.returncode == 0
            and "No local changes" not in stash_result.stdout
        )

        # Create new branch from current HEAD
        run_git("branch", args.branch_name, cwd=source_worktree_path)

        # Create worktree for new branch
        run_git("worktree", "add", str(worktree_path), args.branch_name)

        # If we stashed changes, apply them to the new worktree
        if stashed:
            print_info("  Applying uncommitted changes to new worktree...")
            apply_result = run_git(
                "stash", "apply", "stash@{0}", cwd=worktree_path, check=False
            )
            if apply_result.returncode != 0:
                print_warning(
                    f"Failed to apply stashed changes: {apply_result.stderr}"
                )
                print_warning("Changes remain stashed in source worktree")
            else:
                # Successfully applied, drop from source worktree
                run_git(
                    "stash",
                    "drop",
                    "stash@{0}",
                    cwd=source_worktree_path,
                    check=False,
                )

    else:
        # Fallback
        run_git(
            "worktree",
            "add",
            str(worktree_path),
            "-b",
            args.branch_name,
            args.source_branch,
        )

    # Setup Python virtual environment
    print()
    try:
        setup_python_venv(worktree_path)
    except RuntimeError as e:
        print_error(str(e))
        print_info("Cleaning up worktree...")
        try:
            run_git("worktree", "remove", str(worktree_path), "--force")
            print_info("Worktree removed successfully")
        except Exception as cleanup_error:
            print_warning(f"Failed to clean up worktree: {cleanup_error}")
            print_warning(
                f"Please manually remove: git worktree remove {worktree_path}"
            )
        return 1

    # Print success summary
    print()
    print_success("=" * 60)
    print_success("Worktree created successfully!")
    print_success("=" * 60)
    print()
    print_info("Worktree details:")
    print(f"  Location:     {worktree_path}")
    print(f"  Branch:       {args.branch_name}")
    print(f"  Source:       {args.source_branch}")
    print()
    print_info("Python environment:")
    print("  .venv/        Isolated virtual environment")
    print("  Dependencies: Installed via uv sync")
    print()
    print_info("Next steps:")
    print(f"  cd {worktree_path}")
    print("  # Start development in the new worktree")
    print()
    print_info("To view all worktrees:")
    print("  git worktree list")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

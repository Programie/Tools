#! /usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path
from typing import List


class Git:
    def __init__(self, path: Path):
        self.path = path

    def get_url(self):
        return subprocess.check_output(["git", "-C", self.path, "remote", "get-url", "origin"]).decode("utf-8").strip()

    def set_url(self, url: str):
        return subprocess.check_call(["git", "-C", self.path, "remote", "set-url", "origin", url])

    def clone(self, url):
        subprocess.run(["git", "clone", url, self.path])

    def pull(self):
        subprocess.run(["git", "-C", self.path, "pull"])

    def exists(self):
        return self.path.joinpath(".git").is_dir()


def get_git_paths(base_path: Path, excludes: List[str]):
    for git_path in base_path.rglob("*/.git"):
        if "checkout" in git_path.parts or "vendor" in git_path.parts:
            continue

        repo_path = git_path.parent

        if check_excludes(str(repo_path.relative_to(base_path)), excludes):
            continue

        yield repo_path


def check_excludes(path: str, excludes: List[str]):
    for exclude in excludes:
        if exclude.endswith("/"):
            if path.startswith(exclude):
                return True
        else:
            if path == exclude:
                return True

    return False


def store_repos(base_path: Path, output_file: Path, excludes: List[str]):
    repos = []

    for repo_path in get_git_paths(base_path, excludes):
        relative_path = repo_path.relative_to(base_path)

        git = Git(repo_path)

        repos.append({
            "path": relative_path,
            "url": git.get_url()
        })

    repos.sort(key=lambda item: str(item["path"]).lower())

    with output_file.open("w") as output_file:
        for repo in repos:
            repo_path = repo["path"]
            repo_url = repo["url"]

            output_file.write(f"{repo_path}|{repo_url}\n")


def restore_repos(base_path: Path, input_file: Path, excludes: List[str], purge_unlisted: bool, dry_run: bool, pull: bool):
    listed_paths = set()

    with input_file.open("r") as input_file:
        for line in input_file:
            line = line.strip()

            repo_path, repo_url = line.split("|")

            if check_excludes(repo_path, excludes):
                continue

            listed_paths.add(repo_path)

            full_path = base_path.joinpath(repo_path)

            git = Git(full_path)

            if git.exists():
                existing_repo_url = git.get_url()

                if existing_repo_url != repo_url:
                    if dry_run:
                        print(f"Would change repo url for {full_path}: {existing_repo_url} -> {repo_url}")
                    else:
                        git.set_url(repo_url)

                if pull:
                    if dry_run:
                        print(f"Would pull {full_path}")
                    else:
                        git.pull()
            else:
                if dry_run:
                    print(f"Would clone {repo_url} to {full_path}")
                else:
                    git.clone(repo_url)

    if not purge_unlisted:
        return

    paths_to_purge = set()

    for repo_path in get_git_paths(base_path, excludes):
        relative_path = repo_path.relative_to(base_path)

        if str(relative_path) not in listed_paths:
            paths_to_purge.add(repo_path)

    if not paths_to_purge:
        return

    print("The following folders will be purged:")

    print("")

    for path in paths_to_purge:
        print(f"  {path}")

    print("")

    if input("Are you sure to continue? (y/N) ").lower() != "y":
        return

    for path in paths_to_purge:
        if dry_run:
            print(f"Would remove {path}")
        else:
            shutil.rmtree(path)


def main():
    arg_parser = argparse.ArgumentParser()

    action_parser = arg_parser.add_subparsers(dest="action", required=True)

    store_parser = action_parser.add_parser("store")
    store_parser.add_argument("base_path")
    store_parser.add_argument("output_file")
    store_parser.add_argument("--exclude", nargs="*", default=[])

    restore_parser = action_parser.add_parser("restore")
    restore_parser.add_argument("base_path")
    restore_parser.add_argument("input_file")
    restore_parser.add_argument("--exclude", nargs="*", default=[])
    restore_parser.add_argument("--purge", action="store_true")
    restore_parser.add_argument("--dryrun", action="store_true")
    restore_parser.add_argument("--pull", action="store_true")

    arguments = arg_parser.parse_args()

    if arguments.action == "store":
        store_repos(Path(arguments.base_path).expanduser(), Path(arguments.output_file).expanduser(), excludes=arguments.exclude)
    elif arguments.action == "restore":
        restore_repos(Path(arguments.base_path).expanduser(), Path(arguments.input_file).expanduser(), excludes=arguments.exclude, purge_unlisted=arguments.purge, dry_run=arguments.dryrun, pull=arguments.pull)


if __name__ == "__main__":
    main()

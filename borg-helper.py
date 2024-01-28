#! /usr/bin/env python3

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class ConfigError(RuntimeError):
    pass


class BorgHelper:
    def __init__(self):
        self.config_paths = [
            "/etc/borg-helper.json",
            "~/.config/borg-helper.json",
            "borg-helper.json"
        ]

        self.borg_binary = "borg"
        self.repositories = {}

    def load_configs(self) -> None:
        for path in self.config_paths:
            self.load_config(Path(path).expanduser())

    def load_config(self, path: Path) -> bool:
        if not path.is_file():
            return False

        with path.open("r") as config_file:
            config = json.load(config_file)

            if "borg_binary" in config:
                self.borg_binary = config["borg_binary"]

            for repository_name, repository_config in config.get("repositories", {}).items():
                self.add_repository(repository_name, repository_config)

        return True

    def add_repository(self, name: str, config: dict) -> None:
        if name not in self.repositories:
            self.repositories[name] = {}

        self.repositories[name].update(config)

    def get_repositories(self) -> dict:
        return self.repositories

    def get_repository(self, name: str) -> Optional[dict]:
        return self.repositories.get(name)

    def execute_borg(self, repository_name: str, arguments: list[str]) -> int:
        borg_env = os.environ.copy()
        repository_config = self.get_repository(repository_name)

        if repository_config is None:
            raise ConfigError(f"Unknown repository: {repository_name}")

        if "repository" in repository_config:
            borg_env["BORG_REPO"] = repository_config["repository"]

        if "passphrase" in repository_config:
            borg_env["BORG_PASSPHRASE"] = repository_config["passphrase"]

        if "ssh_key" in repository_config:
            borg_env["BORG_RSH"] = f"ssh -i '{repository_config['ssh_key']}'"

        command_line = [self.borg_binary] + arguments

        print(f"> \033[0;32m{subprocess.list2cmdline(command_line)}\033[0m", file=sys.stderr)

        with subprocess.Popen(command_line, env=borg_env) as borg_process:
            borg_process.wait()

            return borg_process.returncode


def main():
    if len(sys.argv) == 1:
        print("Usage: {} <repository> [borg arguments]".format(sys.argv[0]), file=sys.stderr)
        print("       {} list".format(sys.argv[0]), file=sys.stderr)
        return 1

    borg_helper = BorgHelper()
    borg_helper.load_configs()

    repositories = borg_helper.get_repositories()

    if not repositories:
        print("No repositories configured!", file=sys.stderr)
        return 1

    if sys.argv[1] == "list":
        print("Available repositories:")

        for repository_name in sorted(repositories.keys()):
            print("  {} ({})".format(repository_name, repositories[repository_name]["repository"]))

        return 0

    try:
        return borg_helper.execute_borg(sys.argv[1], sys.argv[2:])
    except ConfigError as error:
        print(error, file=sys.stderr)


if __name__ == "__main__":
    exit(main())

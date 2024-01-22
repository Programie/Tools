#! /usr/bin/env python3

import json
import os
import subprocess
import sys

with open("/etc/borg-helper.json", "r") as config_file:
    repos = json.load(config_file)

if len(sys.argv) == 1:
    print("Usage: {} <repo> [borg arguments]".format(sys.argv[0]), file=sys.stderr)
    print("       {} list".format(sys.argv[0]), file=sys.stderr)
    exit(1)

repo_name = sys.argv[1]

if repo_name == "list":
    print("Available repos:")
    for repo in sorted(repos.keys()):
        print("  {} ({})".format(repo, repos[repo]["repo"]))

    exit(0)

if repo_name not in repos:
    print("Invalid repo name: {}".format(repo_name), file=sys.stderr)
    exit(1)

repo = repos[repo_name]

borg_env = os.environ.copy()

if "repo" in repo:
    borg_env["BORG_REPO"] = borg_repo = repo["repo"]

if "passphrase" in repo:
    borg_env["BORG_PASSPHRASE"] = repo["passphrase"]

if "ssh_key" in repo:
    borg_env["BORG_RSH"] = "ssh -i '{}'".format(repo["ssh_key"])

with subprocess.Popen(["/usr/local/bin/borg"] + sys.argv[2:], env=borg_env) as borg_process:
    borg_process.wait()

    exit(borg_process.returncode)

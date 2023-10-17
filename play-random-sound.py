#! /usr/bin/env python3

import os
import random
import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: {} <path>".format(sys.argv[0]))
    exit(1)

path = os.path.expanduser(sys.argv[1])
state_file = "/tmp/last-random-sound"

if os.path.exists(state_file):
    with open(state_file, "r") as file_handle:
        last_random_file = file_handle.readline()
else:
    last_random_file = None

found_files = []

for root, dirs, files in os.walk(path):
    for file_name in files:
        found_files.append(os.path.join(root, file_name))

if found_files:
    random_file = None

    for _ in range(10):
        random_file = random.choice(found_files)

        if random_file != last_random_file:
            break

    if random_file:
        with open(state_file, "w") as file_handle:
            file_handle.write(random_file)

        subprocess.call(["ffplay", "-nodisp", "-autoexit", random_file])

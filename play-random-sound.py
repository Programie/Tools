#! /usr/bin/env python3

import os
import random
import signal
import subprocess
import sys


class PidFile:
    def __init__(self, path):
        self.path = path

    def get_pid_from_file(self):
        if not os.path.exists(self.path):
            return None

        with open(self.path, "r") as pid_file:
            pid = int(pid_file.readline().strip())
            if not pid:
                return None

        return pid

    def is_process_running(self, search_cmdline: str):
        pid = self.get_pid_from_file()
        if not pid:
            return False

        proc_file = "/proc/{}/cmdline".format(pid)

        if os.path.exists(proc_file):
            with open(proc_file, "r") as cmdline:
                if search_cmdline in cmdline.readline().strip():
                    return True

        return False

    def kill(self):
        pid = self.get_pid_from_file()
        if not pid:
            return

        os.kill(pid, signal.SIGTERM)

    def create(self, pid: int):
        with open(self.path, "w") as pid_file:
            pid_file.write(str(pid))


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <path>".format(sys.argv[0]))
        exit(1)

    path = os.path.expanduser(sys.argv[1])
    state_file = "/tmp/last-random-sound"
    pid_file = PidFile("/tmp/play-random-sound.pid")

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

            if pid_file.is_process_running("ffplay"):
                pid_file.kill()

            with subprocess.Popen(["ffplay", "-nodisp", "-autoexit", random_file]) as process:
                pid_file.create(process.pid)
                process.wait()


if __name__ == "__main__":
    main()

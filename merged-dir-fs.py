#! /usr/bin/env python3

import errno
import os
import sys

from fuse import FUSE, Operations, FuseOSError


class MergedDir(Operations):
    def __init__(self, source, mount_point):
        self.source = source
        self.mount_point = mount_point
        self.files = {}

        self.update_dir()

    def update_dir(self):
        self.files = {}

        for current_path, folders, files in os.walk(self.source):
            for file in files:
                self.files[file] = os.path.join(current_path, file)

    def get_path(self, path):
        if path.startswith("/"):
            path = path[1:]

        if path == "":
            return self.source

        if path not in self.files:
            return None

        return self.files[path]

    def getattr(self, path, fh=None):
        full_path = self.get_path(path)
        if not full_path:
            raise FuseOSError(errno.EROFS)

        stat = os.lstat(full_path)
        return dict((key, getattr(stat, key)) for key in ("st_atime", "st_ctime", "st_gid", "st_mode", "st_mtime", "st_nlink", "st_size", "st_uid"))

    def readdir(self, path, fh):
        return [".", ".."] + list(self.files.keys())

    def open(self, path, flags):
        full_path = self.get_path(path)
        if not full_path:
            raise FuseOSError(errno.EROFS)

        return os.open(full_path, flags)

    def read(self, path, size, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, size)

    def release(self, path, fh):
        return os.close(fh)


def main():
    if len(sys.argv) != 3:
        print("Usage: {} <source> <mountpoint>".format(sys.argv[0]))
        exit(1)

    source = sys.argv[1]
    mountpoint = sys.argv[2]

    FUSE(MergedDir(source, mountpoint), mountpoint, nothreads=True, foreground=True)


if __name__ == "__main__":
    main()

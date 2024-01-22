# merged-dir-fs

merged-dir-fs makes use of FUSE (Filesystem in Userspace) to mount a source directory into a destination directory while flattening the directory structure to a single level.

## Example

You have the following directory structure at your source directory:

```
.
├── dir1
│   ├── some-file
│   └── subdir
│       ├── another-file
│       └── file
├── dir2
└── dir3
    ├── even-more-files
    └── some
        └── path
            └── my-file
```

Using that script, the destination directory will have the following directory structure:

```
.
├── another-file
├── even-more-files
├── file
├── my-file
└── some-file
```

## Usage

Make sure to install the Python module [fusepy](https://pypi.org/project/fusepy/): `pip install fusepy`

After that, you are able to mount any directory using `merged-dir-fs.py <source> <destination>`.

The destination directory will contain your flattened directory structure.

**Note:** The destination directory (mount point) must exist before mounting the directory!

**Note:** The destination directory will be mounted read-only. You can't write files to that directory or modify an existing file.
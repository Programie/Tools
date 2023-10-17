#! /usr/bin/env python3

# Taken from https://ikyle.me/blog/2020/add-mp4-chapters-ffmpeg
# Also see https://www.ffmpeg.org/ffmpeg-all.html#Metadata-1
#
# To get fractions of a second in case of 25 fps: 1000/25*frame
# Examples:
# Frame 00 -> fraction = 000
# Frame 10 -> fraction = 400
# Frame 20 -> fraction = 800
# Frame 24 -> fraction = 960
#
# Example input (last line is only used for time):
# 0:00:00.000 Chapter 1
# 0:23:20.000 Chapter 2
# 0:40:30.000 Chapter 3
# 0:40:56.000 Chapter 4
# 1:04:44.000 Chapter 5
# 1:20:00.000 END
#
# Usage:
# cat Chapters.txt | ffmpeg-chapters.py > Chapters.ffmeta
# ffmpeg -i INPUT.mp4 -i Chapters.ffmeta -map_metadata 1 -map_chapters 1 -codec copy OUTPUT.mp4

import fileinput
import re
import sys

chapters = []

for line in fileinput.input():
    line = line.strip()

    if not line:
        continue

    line_match = re.match(r"(\d+):(\d{2}):(\d{2}\.\d{3}) (.*)$", line)
    if line_match is None:
        print("Unable to parse line: {}".format(line), file=sys.stderr)
        continue

    hours = int(line_match.group(1))
    minutes = int(line_match.group(2))
    seconds = float(line_match.group(3))
    title = line_match.group(4)

    minutes = (hours * 60) + minutes
    seconds = seconds + (minutes * 60)
    timestamp = int(seconds * 1000)

    chapters.append({
        "title": title,
        "startTime": timestamp
    })

for index, chapter in enumerate(chapters):
    if index == len(chapters) - 1:
        break

    print("[CHAPTER]")
    print("TIMEBASE=1/1000")
    print("START={}".format(chapter["startTime"]))
    print("END={}".format(chapters[index + 1]["startTime"] - 1))
    print("title={}".format(chapter["title"]))

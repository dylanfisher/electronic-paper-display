#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Raspberry Pi Electronic Paper Display host sync script.
# This script is intended to be run from a cron job every N minutes.
# The script chooses a random image from a directory and syncs it across
# a series of Raspberry Pi devices. Those Pi devices pick up on the new
# file and automatically display it on their EPD display.

import os
import random
import sys
import signal
import subprocess
from datetime import datetime

def exithandler(signum, frame):
  sys.exit()

def is_supported_filetype(file):
  _, ext = os.path.splitext(file)
  return ext.lower() in [".jpeg", ".jpg"]

signal.signal(signal.SIGTERM, exithandler)
signal.signal(signal.SIGINT, exithandler)

# Configure variables
today = datetime.now()
current_hour = int(today.strftime("%H"))

# Ensure this is the correct path to your files directory
file_dir = os.path.join(os.path.expanduser("~"), "Pictures")
if not os.path.isdir(file_dir):
  os.mkdir(file_dir)

# Pick a random file recursively from the file directory
files = list(filter(is_supported_filetype, [os.path.join(dp, f) for dp, dn, fn in os.walk(file_dir) for f in fn]))
if not files:
  print("No files found")
  sys.exit()

random_file = os.path.join(file_dir, random.choice(files))

devices = [
  "pi@10.0.0.20",
  "pi@10.0.0.21",
  "pi@10.0.0.22",
  "pi@10.0.0.23"
]

# Sync the image across devices, run the commands in parallel
processes = []
for device in devices:
  command = "scp " + random_file + " " + device + ":~/epd_images/image.jpg"
  process = subprocess.Popen(command, shell=True)
  processes.append(process)

# Collect process statuses
output = [p.wait() for p in processes]

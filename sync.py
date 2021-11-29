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
import shutil
import fileinput
from pprint import pprint
from datetime import datetime
from PIL import Image

def exithandler(signum, frame):
  sys.exit()

def is_supported_filetype(file):
  _, ext = os.path.splitext(file)
  return ext.lower() in [".jpeg", ".jpg"]

def print_to_stdout(*a):
  print(*a, file = sys.stdout)

signal.signal(signal.SIGTERM, exithandler)
signal.signal(signal.SIGINT, exithandler)

# Configure variables
today = datetime.now()
current_hour = int(today.strftime("%H"))

# Don't sync between early morning hours
if current_hour > 3 and current_hour < 8:
  sys.exit()

# Create the temporary directories if necessary
tmp_dir = os.path.join(os.path.expanduser("~"), "epd/tmp")
if not os.path.isdir(tmp_dir):
  os.mkdir(tmp_dir)

tmp_dir = os.path.join(os.path.expanduser("~"), "epd/tmp/images")
if not os.path.isdir(tmp_dir):
  os.mkdir(tmp_dir)

tmp_image_dir_name = today.strftime("%Y-%m-%d")
tmp_image_dir = os.path.join(os.path.expanduser("~"), "epd/tmp/images", tmp_image_dir_name)
if not os.path.isdir(tmp_image_dir):
  os.mkdir(tmp_image_dir)

tmp_image_dir_subfolders = [ f.path for f in os.scandir(os.path.join(os.path.expanduser("~"), "epd/tmp/images")) if f.is_dir() ]
for d in tmp_image_dir_subfolders:
  if d == tmp_image_dir:
    # Create a file list of random images from the NAS server sync with this day's images
    if not os.path.exists(tmp_image_dir + "/file_list.txt"):
      with open(tmp_image_dir + "/file_list.txt", "w") as f:
        process = subprocess.Popen("ssh dylan@10.0.0.3 \"cd /volume1/main/photos/lightroom_processed_jpeg; find . -type f -name '*.jpg' | shuf -n 100\"", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        remote_files = process.communicate()[0]
        f.write(remote_files)
    # Read the file list and check if the jpg has already been synced. If the jpg doesn't exist, use scp to copy the file over to the Raspberry Pi
    with open(tmp_image_dir + "/file_list.txt", "r") as f:
      for line in f:
        filename = line.rstrip().split('/')[-1]
        if not os.path.exists(tmp_image_dir + "/" + filename):
          # It would be easier to use rsync here, but the NAS permissions are set up in such a way where ssh key login is not working
          process = subprocess.Popen("scp dylan@10.0.0.3:/volume1/main/photos/lightroom_processed_jpeg/" + line.rstrip() + " " + tmp_image_dir, shell=True)
          process.wait()
    continue
  else:
    shutil.rmtree(d)

# Pick a random file recursively from the image directory
files = list(filter(is_supported_filetype, [os.path.join(dp, f) for dp, dn, fn in os.walk(tmp_image_dir) for f in fn]))
if not files:
  print("No files found")
  sys.exit()

random_file = random.choice(files)

devices = [
  "pi@10.0.0.20",
  "pi@10.0.0.21",
  "pi@10.0.0.22",
  "pi@10.0.0.23"
]

# Open image in PIL (Python Imaging Library)
pil_img = Image.open(random_file)
img_width, img_height = pil_img.size

# Resize the original source image to be a bit smaller
max_size = 3200
if (img_width > max_size) or (img_height > max_size):
  pil_img.thumbnail((max_size, max_size), Image.ANTIALIAS)
  pil_img.save(tmp_dir + "/resized_thumbnail.jpg", "JPEG")

# Sync the image across devices, run the commands in parallel
processes = []
for device in devices:
  processes.append(subprocess.Popen("rsync -aP --rsync-path='mkdir -p ~/epd/tmp/synced_images && rsync' " + tmp_dir + "/resized_thumbnail.jpg" + " " + device + ":~/epd/tmp/synced_images/; ssh " + device + " /usr/bin/python3 /home/pi/epd/images.py", shell=True))

# Collect process statuses
output = [p.wait() for p in processes]

sys.exit()

#!/usr/bin/python3
# -*- coding:utf-8 -*-

# Electronic paper display (EPD) Python driver from Waveshare
# https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in5_V2.py
#
# Run this script from a cron job every minute

import os
# import time
import random
import sys
import signal
# import ffmpeg
# import math
# import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageFile
from datetime import datetime

# Ensure this is the correct import for your particular screen
from waveshare_epd import epd7in5_V2 as epd_driver

# https://stackoverflow.com/questions/12984426/pil-ioerror-image-file-truncated-with-big-images
ImageFile.LOAD_TRUNCATED_IMAGES = True

def exithandler(signum, frame):
  try:
    epd_driver.epdconfig.module_exit()
  finally:
    sys.exit()

signal.signal(signal.SIGTERM, exithandler)
signal.signal(signal.SIGINT, exithandler)

def is_supported_filetype(file):
  _, ext = os.path.splitext(file)
  return ext.lower() in [".jpeg", ".jpg"]

def print_to_stdout(*a):
  print(*a, file = sys.stdout)

# Configure variables
today = datetime.now()
current_hour = int(today.strftime("%H"))

# Initialize the EPD driver
epd = epd_driver.EPD()
width = epd.width   # 800
height = epd.height # 480
epd.init()

# Clear the screen between the hours of 2am and 8am to prevent potential burn-in
if current_hour > 2 and current_hour < 8:
  epd.Clear()
  epd.sleep()
  sys.exit()

# Ensure this is the correct path to your files directory
temp_file_dir = os.path.join(os.path.expanduser("~"), "epd/tmp/synced_images")
if not os.path.isdir(temp_file_dir):
  os.mkdir(temp_file_dir)

# Pick a file from the file directory
files = list(filter(is_supported_filetype, [os.path.join(dp, f) for dp, dn, fn in os.walk(temp_file_dir) for f in fn]))
if not files:
  print("No files found")
  sys.exit()
current_file = os.path.join(temp_file_dir, files[-1])

# Create an empty PIL image canvas in which to paste the current image
canvas_color = (255, 255, 255)
canvas = Image.new("RGB", (width, height), canvas_color)

# Each Raspberry Pi screen is assigned an index from 1-4. The image passed to this script
# is then cropped and displayed across each screen.
#
# ----------   ----------
# - EPD #1 -   - EPD #2 -
# ----------   ----------
# ----------   ----------
# - EPD #3 -   - EPD #4 -
# ----------   ----------

# Get the index of this display
epd_index = 0
with open(os.path.join(os.path.expanduser("~"), "epd", ".epd_screen_id")) as f:
  epd_index = int(f.read())

# Open image in PIL (Python Imaging Library)
pil_img = Image.open(current_file)
img_width, img_height = pil_img.size

# Set the crop points for each display's image
if epd_index == 1:
  left = random.randint(0, int((img_width / 2) - width))
  top = random.randint(0, int((img_height / 2) - height))
elif epd_index == 2:
  left = random.randint(int(img_width / 2) + 1, img_width - width)
  top = random.randint(0, int(img_height / 2) - height)
elif epd_index == 3:
  left = random.randint(0, int((img_width / 2) - width))
  top = random.randint(int(img_height / 2) + 1, img_height - height)
elif epd_index == 4:
  left = random.randint(int(img_width / 2) + 1, img_width - width)
  top = random.randint(int(img_height / 2) + 1, img_height - height)
else:
  left = 0
  top = 0

right = left + width
bottom = top + height

# Cropped image of above dimension
pil_img = pil_img.crop((left, top, right, bottom))

canvas.paste(pil_img, (0, 0))

# Update the EPD display with our image
epd.display(epd.getbuffer(canvas))

# Remove the files from the temporary epd_images directory
for f in files:
  os.remove(f)

# Turn the EPD display off
epd.sleep()

sys.exit()

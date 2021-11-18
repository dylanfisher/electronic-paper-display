#!/usr/bin/python3
# -*- coding:utf-8 -*-

# Electronic paper display (EPD) Python driver from Waveshare
# https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in5_V2.py
#
# Run this script from a cron job every minute

import os
import glob
import time
import sys
import signal
import ffmpeg
import math
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime

# Ensure this is the correct import for your particular screen
from waveshare_epd import epd7in5_V2 as epd_driver

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
temp_file_dir = os.path.join(os.path.expanduser("~"), "epd_images")
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

# TODO:
# - resize the image to get the current quadrant for the display. Check which display
#   this is based on the presence of an ENV variable.
#
# ---------  ---------
# - Pi #1 -  - Pi #2 -
# ---------  ---------
# ---------  ---------
# - Pi #3 -  - Pi #4 -
# ---------  ---------

# Get the index of this display
epd_index = 0
with open('.epd_screen_id') as f:
  epd_index = int(f.read())

# Open image in PIL. The image must be exactly twice the image dimensions of each EPD screen
pil_img = Image.open(current_file)

# Setting the points for cropped image
left = 0
top = 0
right = 0
bottom = 0

if epd_index == 1:
  right = width
  bottom = height
elif epd_index == 2:
  left = width + 1
  right = width * 2
  bottom = height
elif epd_index == 3:
  top = height + 1
  right = width
  bottom = height * 2
elif epd_index == 4:
  left = width + 1
  top = height + 1
  right = width * 2
  bottom = height * 2

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

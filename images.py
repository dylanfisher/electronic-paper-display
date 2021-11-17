#!/usr/bin/python3
# -*- coding:utf-8 -*-

# Electronic paper display (EPD) Python driver from Waveshare
# https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in5_V2.py
#
# Run this script from a cron job every minute

import os
import time
import sys
import random
import signal
import ffmpeg
import math
import random
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

# Used to generate a gradient
def interpolate(f_co, t_co, interval):
  det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
  for i in range(interval):
    yield [round(f + det * i) for f, det in zip(f_co, det_co)]

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
file_dir = os.path.join(os.path.expanduser('~'), "Pictures")
if not os.path.isdir(file_dir):
  os.mkdir(file_dir)

# Pick a random file recursively from the file directory
files = list(filter(is_supported_filetype, [os.path.join(dp, f) for dp, dn, fn in os.walk(file_dir) for f in fn]))
if not files:
    print("No files found")
    sys.exit()
current_file = os.path.join(file_dir, random.choice(files))

# Create an empty PIL image canvas in which to paste the current image
canvas_color = (255, 255, 255)
canvas = Image.new('RGB', (width, height), canvas_color)

# Open image in PIL
pil_img = Image.open(current_file)
# Resize the image so that it covers the size of the display, without changing the aspect ratio
img_width, img_height = pil_img.size
ratio = (width/float(pil_img.size[0]))
new_height = int((float(img_height)*float(ratio)))
pil_img = pil_img.resize((width, new_height), Image.NEAREST)
canvas.paste(pil_img, (0, int((new_height - height) / -2.0)))

# Update the EPD display with our image
epd.display(epd.getbuffer(canvas))

# Turn the EPD display off
epd.sleep()

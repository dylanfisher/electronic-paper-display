#!/usr/bin/python3
# -*- coding:utf-8 -*-

# Electronic paper display (EPD) Python driver from Waveshare
# https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in5_V2.py

import os
import time
import sys
import random
import signal
import ffmpeg
from PIL import Image

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

# Ensure this is the correct path to your files directory
file_dir = os.path.join(os.path.expanduser('~'), "Pictures")
if not os.path.isdir(file_dir):
  os.mkdir(file_dir)

epd = epd_driver.EPD()
width = epd.width
height = epd.height

epd.init()

# Pick a random .mp4 video in your video directory
files = list(filter(is_supported_filetype, os.listdir(file_dir)))
if not files:
    print("No files found")
    sys.exit()
current_file = os.path.join(file_dir, random.choice(files))

# Open image in PIL
pil_img = Image.open(current_file)

# Resize the image so that it covers the size of the display, without changing the aspect ratio
img_height, img_width = pil_img.size
ratio = (width/float(pil_img.size[0]))
new_height = int((float(img_width)*float(ratio)))
pil_img = pil_img.resize((width, new_height), Image.NEAREST)

# Create an empty PIL image canvas in which to paste the current image
canvas_color = (255, 255, 255)
canvas = Image.new(pil_img.mode, (width, height), canvas_color)
placement_x = 0
placement_y = int((new_height - height) / -2.0)
canvas.paste(pil_img, (placement_x, placement_y))

# Update the EPD display with our image
epd.display(epd.getbuffer(canvas))

# Turn the EPD display off
epd.sleep()

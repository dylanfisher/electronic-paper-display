# Electronic Paper Display

## Hardware

- [800×480, 7.5inch E-Ink display HAT for Raspberry Pi](https://www.waveshare.com/7.5inch-e-paper-hat.htm)
- [Raspberry Pi Zero WH](https://www.raspberrypi.com/products/raspberry-pi-zero/)

## Inspiration

The inspiration and initial code for this project comes from this project: https://github.com/TomWhitwell/SlowMovie

## Installation

Install depdendencies:

- `sudo apt install python3-pip`
- `pip3 install git+https://github.com/waveshare/e-Paper.git#egg=waveshare-epd&subdirectory=RaspberryPi_JetsonNano/python`
- `pip3 install pillow`
- `pip3 install git+https://github.com/robweber/omni-epd.git#egg=omni-epd`

## Scratchpad

### Imagemagick conversions

Resize and crop images to fit the 2x2 EPD display grid

`find . -maxdepth 1 -iname "*.jpg" | xargs -L1 -I{} convert -verbose -thumbnail 1600x960^ -gravity center -extent 1600x960 -unsharp 0x.5 "{}" ~/_resized/"{}"`

Potential idea for cropping into a single point of the image and displaying a particular zoomed-in point on each screen

`find . -maxdepth 1 -iname "*.jpg" | xargs -L1 -I{} convert -extent 800x480 -verbose -quality 50 "{}" ~/_resized/"{}"`

### rsync

Sync resized source images to the Pi host

`rsync -azP ~/_resized/ pi@10.0.0.5:~/Pictures`

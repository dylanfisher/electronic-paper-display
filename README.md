# Electronic Paper Display

## Hardware

- [800×480, 7.5inch E-Ink display HAT for Raspberry Pi](https://www.waveshare.com/7.5inch-e-paper-hat.htm)
- [Raspberry Pi Zero WH](https://www.raspberrypi.com/products/raspberry-pi-zero/)

## Inspiration

The inspiration and initial code for this project comes from this project: https://github.com/TomWhitwell/SlowMovie

## Installation

Make sure SPI is enabled on the Raspberry Pi:

- Run `sudo raspi-config`
- Navigate to `Interface Options` > `SPI`
- Select `<Finish>` to exit. Reboot if prompted.

Install depdendencies:

- `sudo apt install python3-pip`
- `sudo apt install ffmpeg`
- `pip3 install git+https://github.com/waveshare/e-Paper.git#subdirectory=RaspberryPi_JetsonNano/python&egg=waveshare-epd`
- `pip3 install ffmpeg-python`
- `pip3 install pillow`
- `pip3 install git+https://github.com/robweber/omni-epd.git#egg=omni-epd`

## Schedule Cron jobs

On the host Raspberry Pi, schedule a cronjob to call the sync script every few minutes.

`# Run Sync script every 2 minutes, "At every 2nd minute past every hour from 0 through 2 and every hour from 8 through 23."`

`*/2 0-2,8-23 * * * ~/epd/sync.py`

`@reboot ~/epd/sync.py`

### Create/clone epd directories

`git clone git@github.com:dylanfisher/electronic-paper-display.git ~/epd`

`mkdir ~/epd_images`

Create a `.epd_screen_id` file in each of the Raspberry Pi's `epd` directory. Add the index of the display, e.g. `1`, `2`, `3` or `4`.

## Scratchpad

### Imagemagick conversions

Resize and crop images to fit the 2x2 EPD display grid

`find . -maxdepth 1 -iname "*.jpg" | xargs -L1 -I{} convert -verbose -strip -thumbnail 1600x960^ -quality 40 -gravity center -extent 1600x960 -unsharp 0x.5 "{}" ~/_converted/"{}"`

Potential idea for cropping into a single point of the image and displaying a particular zoomed-in point on each screen

`find . -maxdepth 1 -iname "*.jpg" | xargs -L1 -I{} convert -extent 800x480 -verbose -quality 50 "{}" ~/_resized/"{}"`

### rsync

Sync resized source images to the Pi host

`rsync -azP ~/_resized/ pi@10.0.0.5:~/Pictures`

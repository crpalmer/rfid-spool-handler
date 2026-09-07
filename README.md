RFID Spool Handler

# Requirements / Limitations

  * **PRINTERS MUST BE IN LAN MODE**
  * external spools are not currently handled
  * RPI Pico 2 W - e.g. [amazon](https://www.amazon.com/waveshare-Pre-Soldered-Raspberry-Microcontroller-Bluetooth/dp/B0DQ7RYHW7/ref=sr_1_1_sspa?crid=252JPOMJ28PGC&dib=eyJ2IjoiMSJ9.blw309FQt8uRCzqUJSgTrOu6Z-q6z5X3MrFa6N_btNCw2gXEFOQ6Iwia1DWLY8JUAzpbogwrUkNp5qJgM-1_EC_KO409NZLkeJsSUObr6WS5qOyOb6ucK2_kTTzlGJMpI45fBPjvNblKXA4aLwJ9MlZhRgenQLC0KyejWCI443MF3Iv7npJRBk918DieyEHxChDjBaiqaSGl7pgUHn74oshCY8MOjZtqBctDBl1May4.ft7Nx3CQYa6mKZM4R5LBBMRUCTBsGI18Uo7VPzTCRHY)
  * PN532 breakout board - e.g. [amazon](https://www.amazon.com/HiLetgo-Communication-Arduino-Raspberry-Android/dp/B01I1J17LC/ref=sr_1_2_sspa?crid=296OL9ABOY8SE&dib=eyJ2IjoiMSJ9.EJyYKR5jJpXZHhPDa3a7JSQ31N-kkO4ZVj8mQLSVSWGp3xnkm_3bzhOOMsDeGP8R8z0RqVgvMbI5dJ1O0TDVBo8HEj-k8IzYMSNBI2vGKGY4DvGiI4PTERjZXPcZG00ZwgL4WbqoUCXRv5bkD91rQRPBMbh8StB0j6kQDLaQ9406GNu1lzmXpdTZN3PO_tU7hx7ZZBPDXP8Xh2X6kSpRV19-MhWYT_a2xTMCYY0iOFs.Kvkeruzz1Uc2vDOxtk3KNV2kN4h_YOkyU27gwpbHgN4).
  * single neopixel bulb:
    * solderless board: e.g. [amazon](https://www.amazon.com/Breakout-Platine-ws2812b-Independent-Control/dp/B0B73LTNNB/ref=sr_1_4?crid=99D8UP7TN8LQ&dib=eyJ2IjoiMSJ9.qCG2j7MrGe8NUVs69FMxQwy1RoxuvxKbd0-dgy0n-olQr9UgJ40lZgw30dvfBQbZttntv-6xRo1qzQSv6Fdz62LF1d1OZa71AmrVF2AOaNgwB1ONnerlGO-cm1m9Y_jRedfJAnq_VrW7e0RMEXLTu3-wbS7H8Yq-swnlG7s0XQmqAWIoAB9lRjLuwLnDmdhZkp2eQA9lud0UQIhJWA4njxlL5a5gzo0-K7AV1PDrEJ4.7qiIhtf0Xw12g0kRBuBmrt6tFsKKPSEeiwVU-vJ_0nk), or
    * requires soldering: e.g. [amazon](https://www.amazon.com/BTF-LIGHTING-WS2812B-Heatsink-10mm3mm-WS2811/dp/B01DC0J3UM/ref=sr_1_3_sspa?crid=2TNY9K3V4TX58&dib=eyJ2IjoiMSJ9.p9jFrYUJzdMt1XdjCwvEHppT3uGUmH6Kwail3Sl9n-sebDcO12PicK21EAPKrUj_B04YLEWLieVXA6A7s1V5zVnxZKGniociyDzhBlQzuUsnK-AwwmTpnLllyWtDUlrhvmuwNO4KVDmH2WvHUvvbExdkvvzix8lyIidHLTZbIJKepiR0sqGfNLKZv52qqpeDjnefgTF4wuA9z2eNNb3XV5I-tx6u_cT2aQyYClTrDYqjENVkTaE2k5Kj0b0hZ_HLONzAJkbJ83Hd4CZKR1fiaXBeQUZhqJUWPLY6Wc5A5XY.HPJZoxVe_DfumZlB07j6Xs6UqkHFuph5P6dnbNrO6gU&dib_tag=se&keywords=neopixel%2Bsingle&qid=1788784956)

# Initial Setup

On first boot, the WiFi configuration will need to be setup.  When you boot
the PI Pico, it will create an access point.  You need to connect to the AP via
open WiFi network _rfid-spool-handler_.

Open the URL [http://192.168.4.1/wifi](http://192.168.4.1/wifi).  From there you specify your network
SSID and password (if needed).  When you save your WiFi configuration the Pico will
reboot and then you can connected to the local IP address.  

NOTE: You may also optionally specify a hostname.  Whether or not the hostname is useful
depends on your network setup and how your DHCP handles hostnames.  It may be useful
for DNS resolution or it may not

# Configuring Printer(s)

For the RFID Reader to be useful, you'll need to define one or more printers to manage.
For each printer, navigate to the Printers tab.  There you'll have a list of any defined
printers which you can edit/delete and the option to add a new printer.

Each printer that you add will connect via mqtt and the Status page will show you
which filaments and colours you have loaded.

# Filament

BambuSlicer (and OrcaSlicer and other OrcaSlicer derivatives) use a property of the filament
called _filament_id_ to identify the specific filament loaded.  If you don't define filaments
in the _rfid-spool-handler_ it will only be able to show you the generic types and you won't
be able to use the RFID scanner to populate the filament information.

Unfortunately, this critical _filament_id_ property isn't visible in the slicer.  To make it
possible to define the mapping for the _rfid-spool-handler_, it listens to any filament
changes made to any of the printers.  It records the last _filament_id_ configured in the
printer and auto populates the _filament_id_ field when you add a new filament.

Therefore to setup a filament, open the slicer, conect to the printer (devices tab) and
then edit the AMS slot to specify the filament.  Finally, return to the _rfid-spool-handler_
and add a new filament.

# RFID Tags:

The only RFID tag format that is recognized by the scanner are ntag2xx tags written using
the OpenSpool format.  The easiest way to write this data to a RFID tag is to use the
free App "Spool Painter" on an Android device.  I assume a similar alternative is available
for iPhones.

To install a new filament in any of your configured printers, scan the RFID tag with the
rfifd-spool-handler (the light will turn green).  It will wait up to 5 minutes for you to
add the spool to an AMS unit.  After the printer finishes loading the filament (there will
be a brief window where the printer's screen shows an incorrect filament) it will be
populated with the information from the RFID tag.

Note: after scanning the RFID tag, the spool information will be shown in the Status tab
of the web application.

# Installing from git

You need to copy (local to pico):

microdot/src/microdot/microdot.py to /microdot
microdot/src/microdot/utemplate.py to /microdot
micropython_pn532/pn532 to /
utemplate/utemplate to /


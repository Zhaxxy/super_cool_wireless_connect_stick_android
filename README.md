# super_cool_wireless_connect_stick_android
Simple python script to be used with rooted android phones to have a wireless usb flash drive

# Why does this exist?
this is useful if you have a device that only takes stuff via usb mass storage, and having to constantly plug in an out a usb stick from that device to your pc can be annoying, with this you can keep the rooted phone plugged in the device at all times (such as for PS4/PS5 savedatas)

# Prerequisites
* Android device must be rooted
* You must have termux setup
* `su` must be working on termux
* [MSD](https://github.com/chenxiaolong/MSD) must already be setup


# MSD app setup
first of all you want add a new mass storage device and create new writeable disk image and set it up normally with your device to plug into (eg PS4) and then format the usb using that device (ps4 can format it as exfat if you press options on the format as external formatted device) basically you want the phone to be functioning as a usb mass storage device and it to be formated
### it will also tell you the img path, you will need this

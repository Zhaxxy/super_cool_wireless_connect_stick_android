# super_cool_wireless_connect_stick_android
Simple python script to be used with rooted android phones to have a wireless usb flash drive

# Why does this exist?
this is useful if you have a device that only takes stuff via usb mass storage, and having to constantly plug in an out a usb stick from that device to your pc can be annoying, with this you can keep the rooted phone plugged in the device at all times (such as for PS4/PS5 savedatas)

# Prerequisites
* Android device must be rooted
* You must have termux setup
* `su` must be working on termux
* [MSD](https://github.com/chenxiaolong/MSD) must already be setup


# inital MSD app setup
first of all you want add a new mass storage device and create new writeable disk image and set it up normally with your device to plug into (eg PS4) and then format the usb using that device (ps4 can format it as exfat if you press options on the format as external formatted device) basically you want the phone to be functioning as a usb mass storage device and it to be formated
### it will also tell you the img path, you will need this

# initial Termux setup
after you did the msd app stuff, youll need to get the `super_cool_wireless_connect_stick_android.py` file onto termux, after you have done that i recommend putting it in its own folder and cd to that folder, you now need to install some things
```
pkg install util-linux
```

```
pkg install python
```
after installing that, you need to make a venv
```
python3 -m venv venv
```
activate it
```
. venv/bin/activate
```
and pip install pyftpdlib
```
pip install pyftpdlib
```
now run 
```
which python3
```
```
/data/data/com.termux/files/home/venv/bin/python3
```

now you can actually run the command
```
su -c '/data/data/com.termux/files/home/venv/bin/python3 super_cool_wireless_connect_stick_android.py
```
itll start hosting a website on port 10067 where you can then toggle the ftp server and usb mass storage on and off (cant have both at same time to avoid corruptions)
```
after you are done, you need to kill this command, run
su -c "pkill -f '/data/data/com.termux/files/home/venv/bin/python3 super_cool_wireless_connect_stick_android.py'"
```
the command it says here is important and you must run it as even after CRTL + C and even exit Termux itll still be running, this command isnt gonna change as long as your setup does not so you can copy it from the cmd output and run it whenever you want to turn the server off

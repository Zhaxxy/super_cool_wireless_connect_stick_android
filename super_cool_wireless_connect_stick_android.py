from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import os
import threading
from pathlib import Path
import subprocess
import json
import sys

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class FTPHost:
    def __init__(self, directory=".", host="0.0.0.0", port=2121):
        self.directory = os.path.abspath(directory)
        self.host = host
        self.port = port

        self.server = None
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            print("FTP server is already running")
            return

        os.makedirs(self.directory, exist_ok=True)

        authorizer = DummyAuthorizer()

        # Anonymous access with read/write permissions
        authorizer.add_anonymous(
            self.directory,
            perm="elradfmwMT"
        )

        handler = FTPHandler
        handler.authorizer = authorizer
        handler.masquerade_address = None


        self.server = FTPServer(
            (self.host, self.port),
            handler
        )

        # Run FTP server in background thread
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            kwargs={"timeout": 0.5, "blocking": True, "handle_exit": False},
            daemon=True
        )

        self.thread.start()
        print(f"FTP server started on {self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.close_all()
            self.server = None

        if self.thread:
            self.thread.join(timeout=2)
            self.thread = None

        print("FTP server stopped")

    def is_running(self):
        return self.thread is not None and self.thread.is_alive()


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    result = s.getsockname()[0]
    s.close()
    assert isinstance(result,str)
    return result


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global global_is_ftp_server_on
        global ftp
        if self.path == '/toggleftpserver':
            global_is_ftp_server_on = not global_is_ftp_server_on
            if global_is_ftp_server_on:
                msd_umount()
                mount_img_for_ftp()
                ftp.start()
            else:
                ftp.stop()
                unmount_img_for_ftp()
                msd_mount()
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            if global_is_ftp_server_on:
                html = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ON Button</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 100px;
            background: #f4f4f4;
        }

        .button {
            display: inline-block;
            width: 300px;
            padding: 45px 20px;
            background: #28c76f;
            color: white;
            text-decoration: none;
            font-size: 32px;
            font-weight: bold;
            border: 4px solid #15964d;
            border-radius: 8px;
            box-shadow: 0 6px 0 #117a3d;
        }

        .button:hover {
            background: #20b963;
        }

        .button:active {
            transform: translateY(4px);
            box-shadow: 0 2px 0 #117a3d;
        }

        .under-text {
            margin-top: 25px;
            font-size: 20px;
            color: #333;
        }
    </style>
</head>

<body>

    <a href="toggleftpserver" class="button">
        FTP server on
    </a>

    <p class="under-text">
        listening on AAAAAAAAAAAAAAAAAAAAAAAA
    </p>

</body>
</html>
""".replace('AAAAAAAAAAAAAAAAAAAAAAAA',f'ftp://{CURRENT_IP}:{FTP_SERVER_PORT}')
            else:
                html = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OFF Button</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 100px;
            background: #f4f4f4;
        }

        .button {
            display: inline-block;
            width: 300px;
            padding: 45px 20px;
            background: #e74c3c;
            color: white;
            text-decoration: none;
            font-size: 32px;
            font-weight: bold;
            border: 4px solid #b52b20;
            border-radius: 8px;
            box-shadow: 0 6px 0 #922016;
        }

        .button:hover {
            background: #d94132;
        }

        .button:active {
            transform: translateY(4px);
            box-shadow: 0 2px 0 #922016;
        }

        .under-text {
            margin-top: 25px;
            font-size: 20px;
            color: #333;
        }
    </style>
</head>

<body>

    <a href="toggleftpserver" class="button">
        ftp server is off
    </a>

    <p class="under-text">
        it should be acting as usb mass storage now
    </p>

</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            self.wfile.write(html.encode("utf-8"))


CURRENT_IP = get_local_ip()
MNT_POINT = '/data/media/0/super_cool_wireless_connect_stick'
HTTP_SERVER_PORT = 10167
FTP_SERVER_PORT = 10267

global_is_ftp_server_on = False

SFDISK_PATH = Path('/data/data/com.termux/files/usr/bin/sfdisk')
with SFDISK_PATH.open('rb') as f:
    a = f.read(1)
    if not a:
        raise FileNotFoundError(str(SFDISK_PATH))
BLKID_PATH = Path('/data/data/com.termux/files/usr/bin/blkid')
with BLKID_PATH.open('rb') as f:
    a = f.read(1)
    if not a:
        raise FileNotFoundError(str(BLKID_PATH))
LOSETUP_PATH = Path('/system/bin/losetup')
with LOSETUP_PATH.open('rb') as f:
    a = f.read(1)
    if not a:
        raise FileNotFoundError(str(LOSETUP_PATH))
MOUNT_PATH = Path('/system/bin/mount')
with MOUNT_PATH.open('rb') as f:
    a = f.read(1)
    if not a:
        raise FileNotFoundError(str(MOUNT_PATH))
UMOUNT_PATH = Path('/system/bin/umount')
with UMOUNT_PATH.open('rb') as f:
    a = f.read(1)
    if not a:
        raise FileNotFoundError(str(UMOUNT_PATH))
MSD_PATH = Path('/data/adb/modules/com.chiller3.msd/msd-tool.arm64-v8a')
with MSD_PATH.open('rb') as f:
    a = f.read(1)
    if not a:
        raise FileNotFoundError(str(MSD_PATH))

del f
del a


def mount_img_for_ftp():
    global loop_device
    Path(MNT_POINT).mkdir(parents=True, exist_ok=True)
    def get_loop_params(img):
        data = json.loads(subprocess.check_output(
            [SFDISK_PATH, "--json", img],
            text=True,
            
        ))

        partition = data["partitiontable"]["partitions"][0]

        offset = partition["start"] * data["partitiontable"]["sectorsize"]
        size = partition["size"] * data["partitiontable"]["sectorsize"]

        return offset, size


    offset, size = get_loop_params(img_path)

    #print(offset, size)

    result = subprocess.run(
        [BLKID_PATH, "-p", "-s", "TYPE", "-o", "value", "-O", str(offset), img_path],
        capture_output=True,
        text=True,
        check=True
    )

    fs_type = result.stdout.strip()
    #print(fs_type)  # exfat

    result = subprocess.run(
        [LOSETUP_PATH, "-o", str(offset), "-S", str(size), '-fs', img_path],
        capture_output=True,
        text=True,
        check=True
    )

    loop_device = result.stdout.strip()
    #print(loop_device)

    result = subprocess.run(
        [MOUNT_PATH, "-t", fs_type, "-o", 'rw', loop_device, MNT_POINT],
        capture_output=True,
        text=True,
        check=True
    )


def unmount_img_for_ftp():
    global loop_device
    result = subprocess.run(
        [UMOUNT_PATH, MNT_POINT],
        capture_output=True,
        text=True,
        check=True
    )
    result = subprocess.run(
        [LOSETUP_PATH, '-d',loop_device],
        capture_output=True,
        text=True,
        check=False # losetup: /dev/block/loop45: No such device or address it keeps saying this, idk seems to be fine
    )


def msd_mount():
    global img_path
    result = subprocess.run(
        [MSD_PATH, 'client', 'set-mass-storage', '-t', 'disk-rw', '-f',img_path],
        capture_output=True,
        text=True,
        check=True
    )


def msd_umount():
    global img_path
    result = subprocess.run(
        [MSD_PATH, 'client', 'set-mass-storage'],
        capture_output=True,
        text=True,
        check=True
    )



def main() -> None:
    try:
        global img_path
        img_config_path = Path(__file__).parent / 'super_cool_wireless_connect_stick_android_img_path.txt'
        try:
            img_path = Path(img_config_path).read_text().strip()
        except Exception:
            while True:
                img_path_str = input('Please enter the path to your disk.img file (eg /sdcard/Download/disk.img): ').strip()
                if not img_path_str:
                    print('enter something')
                    continue
                try:
                    img_path = Path(img_path_str)
                    with img_path.open('rb') as f:
                        a = f.read(1)
                        if not a:
                            raise FileNotFoundError(str(img_path_str))
                except Exception:
                    print(f'{img_path_str} does not exist, or you did not run the py script correctly')
                    continue
                img_config_path.write_text(img_path.as_posix())
                break

        global ftp
        ftp = FTPHost(
            directory=MNT_POINT,
            host=CURRENT_IP,
            port=FTP_SERVER_PORT
        )
        msd_umount()
        mount_img_for_ftp()
        ftp.start()
        if not global_is_ftp_server_on:
            ftp.stop()
            unmount_img_for_ftp()
            msd_mount()
        server = HTTPServer((CURRENT_IP, HTTP_SERVER_PORT), SimpleHandler)
        print(F'http server on http://{CURRENT_IP}:{HTTP_SERVER_PORT}')
        print('after you are done, you need to kill this command, run')
        print(f'''su -c "pkill -f '{sys.executable} {sys.argv[0]}'"''')
        server.serve_forever()
    finally:
        print('after you are done, you need to kill this command, run')
        print(f'''su -c "pkill -f '{sys.executable} {sys.argv[0]}'"''')


if __name__ == '__main__':
    main()

#-*- coding:utf-8 -*-
from IoT_target.video import VlcPlayer
from gtts import gTTS
import threading
#-*- coding:utf-8 -*-
import time
import subprocess
import socket
from tqdm import tqdm

player = VlcPlayer('--input-repeat=-1', '--mouse-hide-timeout=0')

# 문자열 부울대수로 변화하기
def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

#쓰레드 종료용 시그널 함수
def handler(signum, frame):
    global exitThread
    exitThread = True


def play_media(IN_GPIO, OUT_GPIO):
	IN_GPIO_COMMAND = "cat /sys/class/gpio/gpio{}/value".format(IN_GPIO)
	while not exitThread:
		video_state = str2bool(subprocess.getoutput(IN_GPIO_COMMAND))
		if video_state:
			subprocess.getoutput("echo {0} > /sys/class/gpio/gpio{1}/value".format(1,OUT_GPIO))
			player.play()
		else:
			subprocess.getoutput("echo {0} > /sys/class/gpio/gpio{1}/value".format(0,OUT_GPIO))
			player.pause()



IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def main():
    """ Creating a TCP server socket """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[+] Listening...")

    """ Accepting the connection from the client. """
    conn, addr = server.accept()
    print(f"[+] Client connected from {addr[0]}:{addr[1]}")

    """ Receiving the filename and filesize from the client. """
    data = conn.recv(SIZE).decode(FORMAT)
    item = data.split("_")
    FILENAME = item[0]
    FILESIZE = int(item[1])

    print("[+] Filename and filesize received from the client.")
    conn.send("Filename and filesize received".encode(FORMAT))

    """ Data transfer """
    bar = tqdm(range(FILESIZE), f"Receiving {FILENAME}", unit="B", unit_scale=True, unit_divisor=SIZE)

    with open(f"recv_{FILENAME}", "w") as f:
        while True:
            data = conn.recv(SIZE).decode(FORMAT)
            if not data:
                break
            f.write(data)
            conn.send("Data received.".encode(FORMAT))
            bar.update(len(data))

    """ Closing connection. """
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
import socket
import subprocess
import json
from gtts import gTTS
from video import VlcPlayer
import time as t
import pafy
import logging
from vlc import EventType
import schedule as sch
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('target.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

GPIOOUT = [65, 68, 70, 71, 72, 73, 74, 76]
GPIOIN = [111, 112, 113, 114, 229, 117, 118, 75]
host = "0.0.0.0"
port = 8080
# 문자열 부울대수로 변화하기
video_dic = {111 : "blackscreen.mp4", 112: "blackscreen.mp4", 113 :"blackscreen.mp4" , 114: "blackscreen.mp4", 229: "blackscreen.mp4", 117 : "blackscreen.mp4", 118 : "blackscreen.mp4", 74 : "blackscreen.mp4", 75 : "blackscreen.mp4", None: "blackscreen.mp4"}
out_dic = {111 : None, 112: None, 113 :None , 114: None, 229: None, 117 : None, 118 : None, 74 : None, 75 : None, None: None}
scheduleList = {}
schedule = sch
def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

#쓰레드 종료용 시그널 함수
def sig_handler(signum, frame):
    global exitThread
    exitThread = True

def TTS(IN, data):
    nowTime = t.strftime("%Y%m%d-%H%M%S")
    tts = gTTS(text=data, lang="ko", slow=False)
    fileName=f"{nowTime}.mp3"
    tts.save(fileName)
    video_dic[IN] = fileName

def rtsp(IN, data):
    video = pafy.new(data)
    best = video.getbest()
    video_dic[IN] = best.url

def broadcast(IN, fileName):
    video_dic[IN] = fileName

def video_end_handler(event):
    logger.info("video end reached!")
    global video_sig
    video_sig = True

def scheduler_sig_handler():
    logger.info("scheduler awake!")
    global schedule_sig
    schedule_sig = True

def quit_server(client_addr):
    logger.info("{} was gone".format(client_addr))

if __name__ == "__main__":
    HOST, PORT, bufferSize = "0.0.0.0", 8080 , 1024
    # 서버를 생성합니다. 호스트는 localhost, 포트 번호는 8080
    player = VlcPlayer('--mouse-hide-timeout=0')
    player.add_callback(EventType.MediaPlayerEndReached,video_end_handler)
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setblocking(0)
    UDPServerSocket.bind((HOST,PORT))
    video_sig = False
    schedule_sig = False
    player.play(video_dic[None])
    while(True):
        schedule.run_pending()
        if schedule_sig:
            now_time = t.strftime('%H:%M')
            logger.info("schedule is running!")
            player.play(scheduleList[now_time])
        elif video_sig:
            video_sig = False
            index = None
            for i in GPIOIN:
                in_command = f"cat /sys/class/gpio/gpio{i}/value"
                out_command = f"echo 0 > /sys/class/gpio/gpio{out_dic[i]}/value"
                if str2bool(subprocess.getoutput(in_command)):
                    index = i
                    out_command = f"echo 1 > /sys/class/gpio/gpio{out_dic[i]}/value"
                    break
            subprocess.getoutput(out_command)
            player.play(video_dic[index])
            logger.info(f"in {index} out {out_dic[index]} video {video_dic[index]}")
        try:
            recvdata, addr = UDPServerSocket.recvfrom(bufferSize) 
            data = recvdata.decode("utf-8")
            logger.info(f"{addr} wrote: {data}")
            address = addr
            command = json.loads(data)
            if command["category"] == "schedule":
                try :
                    day = command["day"]
                    time = command["time"]
                    if day == "mon":
                        schedule.every().monday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "tue":
                        schedule.every().tuesday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "wen":
                        schedule.every().wednesday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "thu":
                        schedule.every().thursday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "fri":
                        schedule.every().friday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "sat":
                        schedule.every().saturday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "sun":
                        schedule.every().sunday.at(f"{time}").do(scheduler_sig_handler)
                    elif day == "everyday":
                        schedule.every().day.at(f"{time}").do(scheduler_sig_handler)
                    else:
                        schedule.every().day.at(f"{time}").do(scheduler_sig_handler)
                    scheduleList[time] = command["data"]
                    print(f"{scheduleList}")
                except KeyError as e:
                    scheduleList["00:00"] = data
            elif command["category"] == "TTS":
                TTS(command["GPIO_IN"],command["data"])
            elif command["category"] == "rtsp":
                rtsp(command["GPIO_IN"],command["data"])
            else:
                broadcast(command["GPIO_IN"],command["data"])
            logger.info(video_dic)
            logger.info(out_dic)
        except socket.error:
            pass
        # Ctrl - C 로 종료하기 전까지는 서버는 멈추지 않고 작동

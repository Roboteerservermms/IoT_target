import socket
import subprocess
import json
from gtts import gTTS
from video import VlcPlayer, Media
import time as t
import pafy
import logging
from vlc import EventType
import schedule as sch
from queue import PriorityQueue

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
INPIN = { 111 : 1, 112 : 2, 113 : 3, 114 : 4, 229 : 5, 117 : 6, 118 : 7, 75 : 8 }
OUTPIN = { 1 : 65, 2: 68 , 3 : 70, 4 : 71, 5 : 72, 6 : 73, 7 : 74, 8 : 76 }
host = "0.0.0.0"
port = 8080
# 문자열 부울대수로 변화하기

video_dic = {111 : [], 112: [], 113 :[] , 114: [], 229: [], 117 : [], 118 : [], 74 : [], 75 : [], None: ["blackscreen.mp4"]}
out_dic = {111 : [], 112: [], 113 :[] , 114: [], 229: [], 117 : [], 118 : [], 74 : [], 75 : [], None: []}
scheduleList = {}
schedule = sch
jsonPath = "./json/"
mainJson =None
with open(f'{jsonPath}main.json', 'r') as f:
    mainJson = json.load(f)
def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

#쓰레드 종료용 시그널 함수
def sig_handler(signum, frame):
    global exitThread
    exitThread = True


def TTS(inMsg, mainJson):
    nowTime = t.strftime("%Y%m%d-%H%M%S")
    tts = gTTS(text=inMsg["data"], lang="ko", slow=False)
    fileName=f"{nowTime}.mp3"
    tts.save(fileName)
    m = { "OUTPUT" : inMsg["GPIO_OUT"], "media": fileName }
    mainJson['GPIO'][str(inMsg["GPIO_IN"])].append(m)

def rtsp(inMsg, mainJson):
    m = { "OUTPUT" : inMsg["GPIO_OUT"], "media": inMsg["data"] }
    mainJson['GPIO'][str(inMsg["GPIO_IN"])].append(m)

def broadcast(inMsg, mainJson):
    m = { "OUTPUT" : inMsg["GPIO_OUT"], "media": inMsg["data"] }
    mainJson['GPIO'][str(inMsg["GPIO_IN"])].append(m)

def scheduleAdd(inMsg, mainJson):
    m = { "time" : inMsg["time"], "media": inMsg["data"] }
    mainJson['schedule'][inMsg["day"]].append(m)


def video_end_handler(event):
    logger.info("video end reached!")
    global videoEndSig
    videoEndSig = True

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
    videoEndSig = False
    schedule_sig = False
    exitThread = False
    mediaQ = PriorityQueue()
    player.play("blackscreen.mp4")
    while not exitThread:
        with open(f'{jsonPath}main.json', 'r') as f:
            mainJson = json.load(f)
        schedule.run_pending()
        if schedule_sig:
            try :
                now_day= t.strftime('%A')
                now_time = t.strftime('%H:%M')
                for m in mainJson["schedule"][now_day]:
                    if m["time"] == now_time:
                        addMedia = Media(1,mediaData=m["media"])
                        mediaQ.put(addMedia)
                logger.info("schedule is running!")
            except KeyError:
                schedule_sig = False
        else:
            for i in GPIOIN:
                in_command = f"cat /sys/class/gpio/gpio{i}/value"
                if str2bool(subprocess.getoutput(in_command)):
                    m = mainJson["GPIO"][str(INPIN[i])]
                    for m in mainJson["GPIO"][str(INPIN[i])]:
                        addMedia = Media(3, mediaData=m["media"], gpio=m["OUTPUT"])
                        mediaQ.put(addMedia)
                    break
        if videoEndSig:
            try:
                currentM = mediaQ.get_nowait()
                player.play(currentM.data)
                for index,value in enumerate(currentM.gpio):
                    out_command = f'echo {value} > /sys/class/gpio/gpio{GPIOOUT[index]}/value'
                    subprocess.getoutput(out_command)
                logger.info(f"current status {currentM.data} / {currentM.gpio}")
            except:
                pass
        try:
            recvdata, addr = UDPServerSocket.recvfrom(bufferSize)
            data = recvdata.decode("utf-8")
            logger.info(f"{addr} wrote: {data}")
            address = addr
            msgJson = json.loads(data)
            if msgJson["category"] == "schedule":
                scheduleAdd(msgJson,mainJson)
            elif msgJson["category"] == "TTS":
                TTS(msgJson,mainJson)
            elif msgJson["category"] == "rtsp":
                rtsp(msgJson,mainJson)
            else:
                broadcast(msgJson,mainJson)
            nowTime = t.strftime("%Y%m%d-%H%M%S")
            with open(f"{jsonPath}{nowTime}.json","w") as f:
                json.dump(msgJson, f)
            logger.info(f"The Message is {msgJson}")
            with open(f'{jsonPath}main.json', "w") as f:
                json.dump(mainJson, f)
            # Send a message from a client
            msg = json.dumps(mainJson)
            UDPServerSocket.sendto(bytes(msg,"utf-8"),address)
            logger.info(mainJson)
        except socket.error:
            pass
        # Ctrl - C 로 종료하기 전까지는 서버는 멈추지 않고 작동

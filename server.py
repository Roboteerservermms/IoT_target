from socket import *
import subprocess
import json
from gtts import gTTS
from video import VlcPlayer
import time
import pafy
import logging
from vlc import EventType

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
GPIOIN = [111, 112, 113, 114, 117, 118, 75]  
host = "0.0.0.0"
port = 8080
# 문자열 부울대수로 변화하기
video_dic = {111 : "blackscreen.mp4", 112: "blackscreen.mp4", 112 :"blackscreen.mp4" , 114: "blackscreen.mp4", 117 : "blackscreen.mp4", 118 : "blackscreen.mp4", 74 : "blackscreen.mp4", 75 : "blackscreen.mp4", None: "blackscreen.mp4"}
out_dic = {111 : None, 112: None, 112 :None , 114: None, 117 : None, 118 : None, 74 : None, 75 : None, None: None}

def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")

#쓰레드 종료용 시그널 함수
def sig_handler(signum, frame):
    global exitThread
    exitThread = True

def TTS(GPIOIN, data):
    nowTime = time.strftime("%Y%m%d-%H%M%S")
    tts = gTTS(text=data, lang="ko", slow=False)
    fileName=f"{nowTime}.mp3"
    video_dic[GPIOIN] = fileName

def rtsp(GPIOIN, data):
    video = pafy.new(data)
    best = video.getbest()
    video_dic[GPIOIN] = best

def broadcast(GPIO, fileName):
    video_dic[GPIOIN] = fileName

def gpio_handler(event):
    for i in GPIOIN:
        command = f"cat /sys/class/gpio/gpio{i}/value"
        if str2bool(subprocess.getoutput(command)):
            player.play(video_dic[i])
            subprocess.getoutput(f"echo 1 > /sys/class/gpio/gpio{out_dic[i]}/value")
            break
    player.play(video_dic[None])
        
def json_protocol(msg):
    command = json.loads(msg)
    video_dic[ command["GPIO_IN"] ]  = command["data"]
    logger.info(video_dic)
    out_dic[ command["GPIO_IN"] ] = command["GPIO_OUT"]
    logger.info(out_dic)

def quit_server(client_addr): 
    logger.info("{} was gone".format(client_addr))


# -*- coding: utf-8 -*- 
import socketserver
class MyUDPHandler(socketserver.BaseRequestHandler):
    """ The request handler class for our server. It is instantiated once per connection to the server, and must override the handle() method to implement communication to the client. """
    def handle(self): 
        """ 클라이언트와 연결될 때 호출되는 함수 상위 클래스에는 handle() 메서드가 정의되어 있지 않기 때문에 여기서 오버라이딩을 해야함 """
        data = self.request[0]
        socket = self.request[1]
        logger.info(f"{self.client_address[0]} wrote: {data}")
        json_protocol(data.decode("utf-8"))
        socket.sendto(json.dumps(video_dic).encode("utf-8"), self.client_address)

if __name__ == "__main__": 
    HOST, PORT = "0.0.0.0", 8080 
    # 서버를 생성합니다. 호스트는 localhost, 포트 번호는 8080
    global player
    player = VlcPlayer('--input-repeat=999999', '--mouse-hide-timeout=0')
    player.play(video_dic[None])
    player.add_callback(EventType.MediaPlayerEndReached,gpio_handler)
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    logger.info("waiting for connection...") 
    # Ctrl - C 로 종료하기 전까지는 서버는 멈추지 않고 작동 
    server.serve_forever()


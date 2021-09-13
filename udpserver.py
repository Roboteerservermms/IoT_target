
import queue
import socketserver
import json
from gtts import gTTS
import pafy
import time as t
import threading
from videoHandler import videoThread,Media
from gpioHandler import GPIOThread

jsonPath = "./json/"
mainJson = None
with open('./json/main.json') as json_file:
    mainJson = json.load(json_file)


import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler('server.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# define a subclass of UDPServer

def TTS(inMsg, mainJson):
    nowTime = t.strftime("%Y%m%d-%H%M%S")
    tts = gTTS(text=inMsg["data"], lang="ko", slow=False)
    fileName=f"{nowTime}.mp3"
    tts.save(fileName)
    mainJson['GPIO'][str(inMsg["GPIO_IN"])]["OUTPUT"].extend(inMsg["GPIO_OUT"])
    mainJson['GPIO'][str(inMsg["GPIO_IN"])]["media"].append(fileName)

def rtsp(inMsg, mainJson):
    mainJson['GPIO'][str(inMsg["GPIO_IN"])]["OUTPUT"].extend(inMsg["GPIO_OUT"])
    mainJson['GPIO'][str(inMsg["GPIO_IN"])]["media"].append(inMsg["data"])

def broadcast(inMsg, mainJson):
    mainJson['GPIO'][str(inMsg["GPIO_IN"])]["media"].append(inMsg["data"])
    mainJson['GPIO'][str(inMsg["GPIO_IN"])]["OUTPUT"].extend(inMsg["GPIO_OUT"])

def scheduleAdd(inMsg, mainJson):
    mainJson['schedule'][inMsg["day"]][inMsg["time"]].append(inMsg["data"])

def rmBroadcast(inMsg, mainJson):
    mainJson['schedule'][inMsg["day"]][inMsg["time"]]

class MyUDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        # Receive a message from a client
        logger.info(f"Got an UDP Message from {self.client_address[0]}")
        data = self.request[0].decode("utf-8")
        socket = self.request[1]
        logger.info(f"Got an UDP Message from {data}")
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
        with open("main.json", "w") as f:
            json.dump(mainJson, f)
        logger.info("Got an UDP Message from {}".format(self.client_address[0]))
        # Send a message from a client
        socket.sendto(bytes(json.dumps(mainJson),"utf-8"),self.client_address)

#쓰레드 종료용 시그널 함수
def sig_handler(signum, frame):
    global exitThread
    exitThread = True

if __name__ == "__main__":
    server_IP       = "0.0.0.0"
    server_port     = 8080
    serverAddress   = (server_IP, server_port)
    serverUDP = socketserver.UDPServer(serverAddress, MyUDPHandler)
    serverUDP.serve_forever()
    videoQ = queue.PriorityQueue()
    gpioQ = queue.Queue()
    scheduleQ = queue.Queue()
    videoT = threading.Thread(target=videoThread, args=(exitThread,videoQ))
    videoT.start()
    gpioT = threading.Thread(target=GPIOThread, args=(exitThread, gpioQ))
    gpioT.start()
    while exitThread:
        with open('./json/main.json') as json_file:
            mainJson = json.load(json_file)
        nowweekday = t.strftime("%A")
        nowTime = t.strftime("%H:%M")
        try:
            nowScheduleMedia = mainJson["schedule"][nowweekday][nowTime]
            for v in nowScheduleMedia:
                videoQ.put(Media(1,v))
        except KeyError as e:
            continue
        except ValueError as e:
            continue
        try:
            inGPIO = gpioQ.get_nowait()
            nowGPIOOUT = mainJson["GPIO"][inGPIO]["OUTPUT"]
            nowGPIOMedia = mainJson["GPIO"][inGPIO]["media"]
            for v in nowGPIOMedia:
                videoQ.put(Media(2, v,gpio=nowGPIOOUT))
        except queue.Empty:
            continue
        except KeyError:
            continue

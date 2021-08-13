from socket import *
import subprocess
import json
from gtts import gTTS
from IoT_target.video import VlcPlayer
import time

# Import Twisted mainloop
from twisted.internet import reactor

# Import this package objects
from pysysfs.Controller import Controller
from pysysfs.const import OUTPUT, INPUT, RISING

gpio_controller = Controller()
Controller.available_pins = [65, 68, 70, 71, 72, 73, 74, 75, 76, 111, 112, 113, 114, 117, 118]
GPIOOUT = [111, 112, 113, 114, 117, 118, 75]
GPIOIN = [65, 68, 70, 71, 72, 73, 74, 76]
host = "0.0.0.0"
port = 8080

# 문자열 부울대수로 변화하기
def str2bool(v):
   return str(v).lower() in ("yes", "true", "t", "1")

class Server:
    def __init__(self):
        '''
        broadcast switch case
        '''
        self.dict = {"TTS" : self.TTS, "rtsp": self.rtsp, "file": self.broadcast}
        '''
        gpio setting
        '''
        for i in GPIOOUT: ## OUTPUT
            self.gpio_out.append(gpio_controller.alloc_pins(i,OUTPUT))
        '''
        video setting
        '''
        self.player = VlcPlayer('--input-repeat=-1', '--mouse-hide-timeout=0')
        '''
        server setting
        '''
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((host,port))
        self.server_socket.listen(1)
        self.connectionSocket,self.addr = self.server_socket.accept()
        print(str(self.addr),"에서 접속되었습니다")
    
    def __del__(self):
        self.disconnect()
        return -1

    def disconnect(self):
        self.server_socket.close()
    
    def json_read(self):
        self.nowtime = time.strftime("%Y%m%d-%H%M%S")
        recvJson = json.loads(str(self.rbuff,"utf-8"))
        category = recvJson["Category"]
        data = recvJson["Data"]

        self.dict[category](data)

        for gpio in "-".recvJson['GPIO_IN']:
            globals()['gpio_in_{}'.format(gpio)] = gpio_controller.alloc_pin(gpio, INPUT, self.play(), RISING)
            globals()['gpio_in_{}'.format(gpio)].read()

        recvJson['GPIO_OUT']
        

    def TTS(self, data):
        tts = gTTS(text=data, lang="ko", slow=False)
        fileName="{}.mp3".format(self.nowtime)
        self.player.set_url(fileName)

    def rtsp(self, data):
        self.player.set_url(data)

    def broadcast(self, fileName):
        self.player.set_url(fileName)
    
    def play(self):
        if not self.player.is_playing():
            self.player.play()
        subprocess.getoutput("")


# -*- coding: utf-8 -*- 
import socketserver
class MyTCPHandler(socketserver.BaseRequestHandler):
    """ The request handler class for our server. It is instantiated once per connection to the server, and must override the handle() method to implement communication to the client. """
    def handle(self): 
        """ 클라이언트와 연결될 때 호출되는 함수 상위 클래스에는 handle() 메서드가 정의되어 있지 않기 때문에 여기서 오버라이딩을 해야함 """
        self.data = self.request.recv(1024).strip() 
        print("{} wrote:".format(self.client_address[0]))
        print(self.data) # 영어의 소문자 데이터를 receive 하면 대문자로 변환해 send 
        self.request.sendall(self.data.upper()) 
        
if __name__ == "__main__": 
    HOST, PORT = "0.0.0.0", 8080 
    # 서버를 생성합니다. 호스트는 localhost, 포트 번호는 3000 
    
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler) 
    print("waiting for connection...") 
    # Ctrl - C 로 종료하기 전까지는 서버는 멈추지 않고 작동 
    server.serve_forever()


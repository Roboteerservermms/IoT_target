from socket import *
import subprocess
import json
from IoT_target.video import VlcPlayer


# Import Twisted mainloop
from twisted.internet import reactor

# Import this package objects
from pysysfs.Controller import Controller
from pysysfs.const import OUTPUT, INPUT, RISING

gpio_controller = Controller()
Controller.available_pins = [65, 68, 70, 71, 72, 73, 74, 75, 76, 111, 112, 113, 114, 117, 118]
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
        for i in [111, 112, 113, 114, 117, 118, 75]: ## OUTPUT 
            self.gpio_out.append(gpio_controller.alloc_pins(i,OUTPUT))

        for i in [65, 68, 70, 71, 72, 73, 74, 76]:
            self.gpio_in.append(gpio_controller.alloc_pins(i,INPUT))
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
        recvJson = json.loads(str(self.rbuff,"utf-8"))
        for gpio in "-".recvJson['GPIO_IN']:
            pin = gpio_controller.alloc_pin(gpio, INPUT, self.dict[recvJson['Category']], RISING)

        recvJson['GPIO_OUT']
        

    def TTS(self, number, state):

    def rtsp(self, number, state):

    def broadcast(self, number, state):

#-*- coding:utf-8 -*-
from typing_extensions import IntVar
import paho.mqtt.client as mqtt


def on_message_connect_device(client, userdata, msg):
	global deviceNum
	deviceNum = int(msg.payload)
	print("Device number assigned to {}".format(deviceNum))
	client.message_callback_add('Broadcast/{}/#'.format(), on_message_connect_broadcast)

def on_message_connect_broadcast(client, userdata, msg):
	if rc == 0:
	
	else:
		print("reconnect server please!")
		return -1
	print("Device number assigned to {}".format(deviceNum))
	client.message_callback_add('Broadcast/{}/#'.format())

def on_disconnect(client, userdata, flags, rc=0):
    print("")

#서버로부터 CONNTACK 응답을 받을 때 호출되는 콜백
def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected with result code "+str(rc))
	else:
		print("Bad connection Returned code=", rc)
		return -1

#서버로부터 publish message를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.

## 상수들
client = mqtt.Client() #client 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정
client.on_disconnect = on_disconnect
client.message_callback_add('deviceNum/',on_message_connect_device)
broker_server = ""
recvData = ""
deviceNum = None


if __name__ == '__main__':
	broker_server = input("서버 IP주소를 입력해주세요")
	client.connect(broker_server, 1883, 60) #라즈베리파이3 MQTT 브로커에 연결
	client.loop_forever()
#-*- coding:utf-8 -*-
import paho.mqtt.client as mqtt

#-*- coding:utf-8 -*-
import paho.mqtt.client as mqtt

broker_server = ""
recvData = ""
client = mqtt.Client() #client 오브젝트 생성
#서버로부터 CONNTACK 응답을 받을 때 호출되는 콜백
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("Broadcast/#") #방송 토픽 받기

#서버로부터 publish message를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.


client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정


if __name__ == '__main__':
	broker_server = input("서버 IP주소를 입력해주세요")
	client.connect(broker_server, 1883, 60) #라즈베리파이3 MQTT 브로커에 연결
	client.loop_forever()
#-*- coding:utf-8 -*-
import paho.mqtt.client as mqtt
from gtts import gTTS
import threading
#-*- coding:utf-8 -*-
import vlc
import time

def play_media(args):
	instance = vlc.Instance()
	#Create a MediaPlayer with the default instance
	player = instance.media_player_new()
	player.set_fullscreen(True)
	#Load the media file
	media = instance.media_new('{}'.format(args))
	#Add the media to the player
	player.set_media(media)

	#Play for 10 seconds then exit
	player.play()
	time.sleep(5)



broker_server = ""
recvData = ""
client = mqtt.Client() #client 오브젝트 생성
#서버로부터 CONNTACK 응답을 받을 때 호출되는 콜백
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("Broadcast/#") #방송 토픽 받기

#서버로부터 publish message를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
	recvData = str(msg.payload.decode("utf-8"))
	print(recvData) #토픽과 메세지를 출력한다.
	tts = gTTS(text=recvData, lang="ko", slow=False)
	fileName="helloEN.mp3"
	tts.save(fileName)
	play_media(fileName)
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정


if __name__ == '__main__':
	broker_server = input("서버 IP주소를 입력해주세요: ")
	client.connect(broker_server, 1883, 60) #라즈베리파이3 MQTT 브로커에 연결
	client.loop_forever()

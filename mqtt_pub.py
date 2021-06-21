#-*- coding:utf-8 -*-
import paho.mqtt.client as mqtt

mqtt = mqtt.Client("python_pub") #Mqtt Client 오브젝트 생성
mqtt.connect("192.168.0.12", 1883) #MQTT 서버에 연결
while 1:
    message = input()
    mqtt.publish("Action", message ) #토픽과 메세지 발행
    mqtt.loop(2) #timeout 2sec. 
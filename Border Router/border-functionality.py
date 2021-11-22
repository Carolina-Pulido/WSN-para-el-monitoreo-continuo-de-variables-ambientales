import time
from socket import * #
import socket
from socket import error
import requests
import math

import paho.mqtt.client as mqttClient
import time
import datetime
import json
import random

import csv

'''
global variables
'''

connected = False  # Stores the connection status
BROKER_ENDPOINT = "industrial.api.ubidots.com"
PORT = 1883
MQTT_USERNAME =  "BBFF-yQyzbRB9Mo8Z1Ky1RDiLlsKaLnRTfv"#"BBFF-kk3R4CDlpaN1Xd3oBllFL1zi55c6OZ"  # Put here your TOKEN
MQTT_PASSWORD =  "BBFF-yQyzbRB9Mo8Z1Ky1RDiLlsKaLnRTfv"#"BBFF-kk3R4CDlpaN1Xd3oBllFL1zi55c6OZ"
TOPIC = "/v1.6/devices/"
TOPIC2 = "/v1.6/devices"
DEVICE_LABEL_TIME = "average"
VARIABLE_LABEL_SEND = "envio"
VARIABLE_LABEL_SENSE = "muestras"
DEVICE_LABEL_AVE = "average"
VARIABLE_LABEL_SOIL_AVE = "Humedad del suelo"
VARIABLE_LABEL_TEMP_AVE = "Temperatura"
VARIABLE_LABEL_HUM_AVE = "Humedad ambiente"
HOST = 'fd00::1'
port2 = 5678
direcciones = []
recv_mess = "1"
timestam = []
global wait


'''
Functions to process incoming and outgoing streaming
'''


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[INFO] Connected to broker")
        global connected  # Use global variable
        connected = True  # Signal connection

    else:
        print("[INFO] Error, connection failed")

#Función envío hacia abajo
def on_message(mqttc, obj, msg):
    global t_send, samples
    global hh2
    global hh3
    global send
    
    print("[INFO] value received: {}".format((msg.payload)))
    top = msg.topic
    print(top)
    
    if top == "/v1.6/devices/average/envio/lv":
        t_send = str(int(float(msg.payload))*60)
        hh2= "envio "
        hh3 = hh2 + t_send
        print("valor t_send", hh3)
        print("direcciones", direcciones[0])
        
        if t_send:
            for i in direcciones:
                sent = s.sendto(hh3.encode(), (i, 8765, 0, 0))
                print('sent {} bytes back to {}'.format(sent, (i, 8765, 0, 0)))


    elif top == "/v1.6/devices/average/muestras/lv":
        samples = str(int(float(msg.payload)))
        hh2= "numsensado "
        hh3 = hh2 + samples
        print("valor samples", hh3)
        print("direcciones", direcciones[0])
        
        if samples:
            for i in direcciones:
                sent = s.sendto(hh3.encode(), (i, 8765, 0, 0))
                print('sent {} bytes back to {}'.format(sent, (i, 8765, 0, 0)))
                
 


def on_publish(client, userdata, result):
    print("[INFO] Published!")


def connect(mqtt_client, mqtt_username, mqtt_password, broker_endpoint, port):
    global connected

    if not connected:
        mqtt_client.username_pw_set(mqtt_username, password=mqtt_password)
        mqtt_client.on_message = on_message
        mqtt_client.on_connect = on_connect
        mqtt_client.on_publish = on_publish
        mqtt_client.connect(broker_endpoint, port=port)
        mqtt_client.loop_start()

        attempts = 0

        while not connected and attempts < 5:  # Waits for connection
            print("[INFO] Attempting to connect...")
            time.sleep(1)
            attempts += 1

    if not connected:
        print("[ERROR] Could not connect to broker")
        return False

    return True


def publish(mqtt_client, topic, payload):
    try:
        mqtt_client.publish(topic, payload)
    except Exception as e:
        print("[ERROR] There was an error, details: \n{}".format(e))


def main(mqtt_client):

    # Simulates sensor values
    #sensor_value = random.random() * 100
    global soil_hum
    global addr
    global temp
    global humidity
    global node
    global s   
    
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) #Se usa para crear objetos de socket de la comunidad de red
        s.bind((HOST, port2)) #Se utiliza para vincular direcciones IP y números de puerto a objeto del socket

    except Exception:
        print ('ERROR: Server Port Binding Failed')
        return
    
    print('udp echo server ready: %s' %port2)
    
    print ('Waiting...')
    

    soil_hum, addr = s.recvfrom(1024)
    print("tamaño soil = ",len(soil_hum))
#     samples2 = soil_hum[len(soil_hum)-1] % 10
#     t_send2 = soil_hum[len(soil_hum)-1] - samples2
#     print("moduloooooo", we)
    t_send2 = int (t_send)
    samples2 =int(samples)
    print("TIEMPO DE ENVIO: ", t_send2)
    print("NUM DE MUESTRAS: ", samples2)
    sent = s.sendto(recv_mess.encode(), (addr[0], 8765, 0, 0))
    print('sent {} bytes back to {}'.format(sent, (addr[0], 8765, 0, 0)))
   
    #print(addr)
    current_time = datetime.datetime.now() # datetime.datetime.utcnow()
    print("current_time", current_time)
    
    for i in range(1, samples2, 1):
        xw= int(t_send2 - (i*(t_send2/samples2)))
        time_before= current_time - datetime.timedelta(seconds = xw)
        print("time_before", time_before)
        unix_timestamp = int(time_before.timestamp()) * 1000
        timestam.append(unix_timestamp)
        
    unix_timestamp = int(current_time.timestamp()) * 1000
    timestam.append(unix_timestamp)
    
#     for i in timestam:
#         print(i)


    
    ###Para las tres variables
    
    if addr[0] == 'fd00::212:4b00:615:ab05': ##Node 2 (5)
        node = 2
        DEVICE_LABEL = "Nodo_2_3"
        VARIABLE_LABEL_1 = "Humedad del suelo n2"  # Put your first variable label here
        VARIABLE_LABEL_2 = "Temperatura n2"  # Put your second variable label here
        VARIABLE_LABEL_3 = "Humedad ambiente n2"
        for i in range(0, len(soil_hum), 4):
            print(soil_hum[i])
            var1 = "humedad1"
            var2 = "temperatura"
            var3 = "humedad2"
            guardar_nodo_1([var1, soil_hum[i], var2, soil_hum[i+1], var3, soil_hum[i+2], node])

        aux = 0
        soil_hum = list(soil_hum)
        for i in range(0, len(soil_hum), 4):
            #print(soil_hum[i])
            #Cálculo sensor humedad del suelo
            #mult = (49315^{2})-123076*(70343-(1000*soil_hum[i]))#
            mult = (0.3252*int(soil_hum[i]))#-527.177156
            raiz = math.sqrt(mult)
            soil_percent = (11.762 -raiz)/0.1626
            #soil_hum[i] = ((49315-sqrt(mult))/61538)*100
            
            if(soil_percent >=100):
                soil_hum[i] = 100
            elif(soil_percent <=0):
                soil_hum[i] = 0
            elif(soil_percent > 0 and soil_percent <100):
                soil_hum[i] = soil_percent
                
            payload = json.dumps({VARIABLE_LABEL_1: {'value': soil_hum[i], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_2: {'value': soil_hum[i+1], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_3: {'value': soil_hum[i+2], "timestamp": timestam[i-(3*aux)]}})
        
            topic = "{}{}".format(TOPIC, DEVICE_LABEL)
            if not connected:  # Connects to the broker
                connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                        BROKER_ENDPOINT, PORT)

            # Publishes values
            print("[INFO] Attempting to publish payload:")
            print(payload)
            publish(mqtt_client, topic, payload)
            aux = aux + 1
            
            if i == (len(soil_hum)-4):
                payload = json.dumps({VARIABLE_LABEL_SOIL_AVE: soil_hum[i],
                                  VARIABLE_LABEL_TEMP_AVE: soil_hum[i+1],
                                  VARIABLE_LABEL_HUM_AVE: soil_hum[i+2]})
            
                topic = "{}{}".format(TOPIC, DEVICE_LABEL_AVE)
                if not connected:  # Connects to the broker
                    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                            BROKER_ENDPOINT, PORT)

                # Publishes values
                print("[INFO] Attempting to publish payload:")
                print(payload)
                publish(mqtt_client, topic, payload)
        timestam.clear()    
    
        
    elif addr[0] == 'fd00::212:4b00:615:9650': ##Node 3 (7)
        node = 3
        DEVICE_LABEL = "Nodo_2_3"
        for i in range(0, len(soil_hum), 4):
            print(soil_hum[i])
            var1 = "humedad1"
            var2 = "temperatura"
            var3 = "humedad2"
            guardar_nodo_2([var1, soil_hum[i], var2, soil_hum[i+1], var3, soil_hum[i+2], node])
        VARIABLE_LABEL_1 = "Humedad del suelo n3"  # Put your first variable label here
        VARIABLE_LABEL_2 = "Temperatura n3"  # Put your second variable label here
        VARIABLE_LABEL_3 = "Humedad ambiente n3"
        aux = 0
        soil_hum = list(soil_hum)
        for i in range(0, len(soil_hum), 4):
            #print(soil_hum[i])
            #Cálculo sensor humedad del suelo
            mult = (0.3252*int(soil_hum[i]))#-527.177156
            raiz = math.sqrt(mult)
            soil_percent = (11.762 -raiz)/0.1626
            
            if(soil_percent >=100):
                soil_hum[i] = 100
            elif(soil_percent <=0):
                soil_hum[i] = 0
            elif(soil_percent > 0 and soil_percent <100):
                soil_hum[i] = soil_percent
                
            payload = json.dumps({VARIABLE_LABEL_1: {'value': soil_hum[i], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_2: {'value': soil_hum[i+1], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_3: {'value': soil_hum[i+2], "timestamp": timestam[i-(3*aux)]}})
        
            topic = "{}{}".format(TOPIC, DEVICE_LABEL)
            if not connected:  # Connects to the broker
                connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                        BROKER_ENDPOINT, PORT)

            # Publishes values
            print("[INFO] Attempting to publish payload:")
            print(payload)
            publish(mqtt_client, topic, payload)
            aux = aux + 1
            
            if i == (len(soil_hum)-4):
                payload = json.dumps({VARIABLE_LABEL_SOIL_AVE: soil_hum[i],
                                  VARIABLE_LABEL_TEMP_AVE: soil_hum[i+1],
                                  VARIABLE_LABEL_HUM_AVE: soil_hum[i+2]})
            
                topic = "{}{}".format(TOPIC, DEVICE_LABEL_AVE)
                if not connected:  # Connects to the broker
                    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                            BROKER_ENDPOINT, PORT)

                # Publishes values
                print("[INFO] Attempting to publish payload:")
                print(payload)
                publish(mqtt_client, topic, payload)
        timestam.clear()
            
   
        
    elif addr[0] == 'fd00::212:4b00:615:9fe3': ##Node 4 (6)
        node = 4
        DEVICE_LABEL = "Nodo_4_5"
        for i in range(0, len(soil_hum), 4):
            print(soil_hum[i])
            var1 = "humedad1"
            var2 = "temperatura"
            var3 = "humedad2"
            guardar_nodo_3([var1, soil_hum[i], var2, soil_hum[i+1], var3, soil_hum[i+2], node])
        VARIABLE_LABEL_1 = "Humedad del suelo n4"  # Put your first variable label here
        VARIABLE_LABEL_2 = "Temperatura n4"  # Put your second variable label here
        VARIABLE_LABEL_3 = "Humedad ambiente n4"
        aux = 0
        soil_hum = list(soil_hum)
        for i in range(0, len(soil_hum), 4):
            #print(soil_hum[i])
            #Cálculo sensor humedad del suelo
            mult = (0.3252*int(soil_hum[i]))#-527.177156
            raiz = math.sqrt(mult)
            soil_percent = (11.762 -raiz)/0.1626
            
            if(soil_percent >=100):
                soil_hum[i] = 100
            elif(soil_percent <=0):
                soil_hum[i] = 0
            elif(soil_percent > 0 and soil_percent <100):
                soil_hum[i] = soil_percent
                
            payload = json.dumps({VARIABLE_LABEL_1: {'value': soil_hum[i], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_2: {'value': soil_hum[i+1], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_3: {'value': soil_hum[i+2], "timestamp": timestam[i-(3*aux)]}})
        
            topic = "{}{}".format(TOPIC, DEVICE_LABEL)
            if not connected:  # Connects to the broker
                connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                        BROKER_ENDPOINT, PORT)

            # Publishes values
            print("[INFO] Attempting to publish payload:")
            print(payload)
            publish(mqtt_client, topic, payload)
            aux = aux + 1
            
            if i == (len(soil_hum)-4):
                payload = json.dumps({VARIABLE_LABEL_SOIL_AVE: soil_hum[i],
                                  VARIABLE_LABEL_TEMP_AVE: soil_hum[i+1],
                                  VARIABLE_LABEL_HUM_AVE: soil_hum[i+2]})
            
                topic = "{}{}".format(TOPIC, DEVICE_LABEL_AVE)
                if not connected:  # Connects to the broker
                    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                            BROKER_ENDPOINT, PORT)

                # Publishes values
                print("[INFO] Attempting to publish payload:")
                print(payload)
                publish(mqtt_client, topic, payload)
        timestam.clear()
        
    elif addr[0] == 'fd00::212:4b00:615:ab70': #'fd00::212:4b00:616:f49': #Node 5 (8)
        node = 5
        DEVICE_LABEL = "Nodo_4_5"
        for i in range(0, len(soil_hum), 4):
            print(soil_hum[i])
            var1 = "humedad1"
            var2 = "temperatura"
            var3 = "humedad2"
            guardar_nodo_4([var1, soil_hum[i], var2, soil_hum[i+1], var3, soil_hum[i+2], node])
        VARIABLE_LABEL_1 = "Humedad del suelo n5"  # Put your first variable label here
        VARIABLE_LABEL_2 = "Temperatura n5"  # Put your second variable label here
        VARIABLE_LABEL_3 = "Humedad ambiente n5"
        aux = 0
        soil_hum = list(soil_hum)
        for i in range(0, len(soil_hum), 4):
            #print(soil_hum[i])
            #Cálculo sensor humedad del suelo
            mult = (0.3252*int(soil_hum[i]))#-527.177156
            raiz = math.sqrt(mult)
            soil_percent = (11.762 -raiz)/0.1626
            
            if(soil_percent >=100):
                soil_hum[i] = 100
            elif(soil_percent <=0):
                soil_hum[i] = 0
            elif(soil_percent > 0 and soil_percent <100):
                soil_hum[i] = soil_percent
                
            payload = json.dumps({VARIABLE_LABEL_1: {'value': soil_hum[i], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_2: {'value': soil_hum[i+1], "timestamp": timestam[i-(3*aux)]},
                                  VARIABLE_LABEL_3: {'value': soil_hum[i+2], "timestamp": timestam[i-(3*aux)]}})
        
            topic = "{}{}".format(TOPIC, DEVICE_LABEL)
            if not connected:  # Connects to the broker
                connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                        BROKER_ENDPOINT, PORT)

            # Publishes values
            print("[INFO] Attempting to publish payload:")
            print(payload)
            publish(mqtt_client, topic, payload)
            aux = aux + 1
            
            if i == (len(soil_hum)-4):
                payload = json.dumps({VARIABLE_LABEL_SOIL_AVE: soil_hum[i],
                                  VARIABLE_LABEL_TEMP_AVE: soil_hum[i+1],
                                  VARIABLE_LABEL_HUM_AVE: soil_hum[i+2]})
            
                topic = "{}{}".format(TOPIC, DEVICE_LABEL_AVE)
                if not connected:  # Connects to the broker
                    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                            BROKER_ENDPOINT, PORT)

                # Publishes values
                print("[INFO] Attempting to publish payload:")
                print(payload)
                publish(mqtt_client, topic, payload)
        timestam.clear()
    


def guardar_nodo_1(dato): #Almacena datos de sonido en archivo .csv
    with open('nodo_1_100.csv', mode="a+", newline='') as archivo_nodo_1:
        writer = csv.writer(archivo_nodo_1, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(dato)
#         print("guardó excel")
#         print("dato: ", dato)
        
def guardar_nodo_2(dato): #Almacena datos de sonido en archivo .csv
    with open('nodo_2_100.csv', mode="a+", newline='') as archivo_nodo_2:
        writer = csv.writer(archivo_nodo_2, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(dato)
#         print("guardó excel")
#         print("dato: ", dato)

def guardar_nodo_3(dato): #Almacena datos de sonido en archivo .csv
    with open('nodo_3_100.csv', mode="a+", newline='') as archivo_nodo_3:
        writer = csv.writer(archivo_nodo_3, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(dato)
#         print("guardó excel")
#         print("dato: ", dato)

def guardar_nodo_4(dato): #Almacena datos de sonido en archivo .csv
    with open('nodo_4_100.csv', mode="a+", newline='') as archivo_nodo_4:
        writer = csv.writer(archivo_nodo_4, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(dato)
#         print("guardó excel")
#         print("dato: ", dato)

if __name__ == '__main__':
    

    #direcciones.append('fd00::212:4b00:616:f49')
    direcciones.append('fd00::212:4b00:615:ab70')
    direcciones.append('fd00::212:4b00:615:9fe3')
    direcciones.append('fd00::212:4b00:615:9650')
    direcciones.append('fd00::212:4b00:615:ab05')
    
    
    mqtt_client = mqttClient.Client()
    connect(mqtt_client, MQTT_USERNAME, MQTT_PASSWORD,
                        BROKER_ENDPOINT, PORT)
    topic = "{}/{}/{}/lv".format(TOPIC2, DEVICE_LABEL_TIME, VARIABLE_LABEL_SEND)
    print(topic)
    mqtt_client.subscribe(topic,0)
    
    topich = "{}/{}/{}/lv".format(TOPIC2, DEVICE_LABEL_TIME, VARIABLE_LABEL_SENSE)
    print(topich)
    mqtt_client.subscribe(topich,0)

    mqtt_client.loop_start()
    
    while True:
        
        main(mqtt_client)
        time.sleep(1)

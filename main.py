# Lecturer's code-------------------------------------------------------------------------------------------------------
import requests
import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports
import geolocation

# Lecturer's code-------------------------------------------------------------------------------------------------------
print("Welcome to CO3038, Lab 1.")
BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "FGdNTjaigRJBidqrJZ60"

mess = ""
bbc_port = ""
if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    cmd = -1
    # TODO: Update the cmd to control 2 devices
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            temp_data['valueLED'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if temp_data['valueLED']:
                cmd = 1
            else:
                cmd = 0
        elif jsonobj['method'] == "setPump":
            temp_data['valuePump'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
            if temp_data['valuePump']:
                cmd = 3
            else:
                cmd = 2
    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())


def connected(client, userdate, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection failed!")


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[1] == "TEMP":
            _temp = {'temperature': splitData[2]}
            client.publish('v1/devices/me/telemetry', json.dumps(_temp), 1)
        elif splitData[1] == "LIGHT":
            _humi = {'light': splitData[2]}
            client.publish('v1/devices/me/telemetry', json.dumps(_humi), 1)
        elif splitData[1] == "HUMI":
            _humi = {'humidity': splitData[2]}
            client.publish('v1/devices/me/telemetry', json.dumps(_humi), 1)
    except:
        pass


def readSerial():
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if end == len(mess):
                mess = ""
            else:
                mess = mess[end + 1:]


# Lecturer's code-------------------------------------------------------------------------------------------------------
client = mqttclient.Client("Gateway_Thingsboard")

client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message
# ----------------------------------------------------------------------------------------------------------------------

counter = 0
# -----------------------------------------------------------------------------------------------------------------------
while True:
    if len(bbc_port) > 0:
        readSerial()

    # Get coordinates using WinRT-based functions.
    latitude = geolocation.get_location()[0]
    longitude = geolocation.get_location()[1]

    # Get city name from coordinates using GeoPy.
    where = geolocation.geolocator.reverse(str(latitude) + "," + str(longitude))
    address = where.raw['address']
    city = address.get('city', '')
    state = address.get('state', '')
    country = address.get('country', '')

    # Using OpenWeather API to get dynamic temperature and humidity.
    complete_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={geolocation.api_key}"
    response = requests.get(complete_url)
    response_json = response.json()

    # if response_json["cod"] != "404":
    #     response_json_main = response_json["main"]
    #     # Convert from Kelvin to Celsius.
    #     temp = response_json_main["temp"]-273.15
    #
    #     humi = response_json_main["humidity"]

    # Convert data to JSON.
    collect_data = {'longitude': longitude,
                    'latitude': latitude, 'city': city, 'state': state, 'country': country}

    # Changes light intensity and loops back if overflow.
    # light_intensity += 1
    # if (light_intensity > 100):
    #     light_intensity = 0

    # Send data to server.
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    # Print to console to check.
    print("Current location: ", city, ", ", state, ", ", country)
    time.sleep(10)

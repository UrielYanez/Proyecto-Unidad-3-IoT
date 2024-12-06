from machine import Pin, PWM, ADC
from hcsr04 import HCSR04
from time import sleep
import network
from umqtt.simple import MQTTClient

# Asignación de los pines de LEDs
ledYellow1 = Pin(33, Pin.OUT)
ledYellow2 = Pin(32, Pin.OUT)
ledWhite = Pin(22, Pin.OUT)
ledRed = Pin(2, Pin.OUT)


MQTT_BROKER = "broker.emqx.io"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "armando/uriel"
MQTT_PORT = 1883


# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('UTNG_GUEST', 'R3d1nv1t4d0s#UT')
    while not sta_if.isconnected():
        print(".", end="")
        sleep(0.3)
        print("WiFi Conectada!")

#Funcion para subscribir al broker, topic
def subscribir():
    client = MQTTClient(MQTT_CLIENT_ID,
    MQTT_BROKER, port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    keepalive=0)
    client.set_callback(llegada_mensaje)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("Conectado a %s, en el topico %s"%(MQTT_BROKER, MQTT_TOPIC))
    return client


# Configuración de los pines del Motor A
in1 = Pin(12, Pin.OUT)
in2 = Pin(14, Pin.OUT)
enA = PWM(Pin(13), freq=1000)

# Configuración de los pines del Motor B
in3 = Pin(27, Pin.OUT)
in4 = Pin(26, Pin.OUT)
enB = PWM(Pin(25), freq=1000)

# Asignación del pin del Buzzer
buzzer = PWM(Pin(23))
buzzer.freq(1000)
buzzer.duty(0)

sensorFront = HCSR04(trigger_pin=21, echo_pin=19, echo_timeout_us=24000)
sensorBack = HCSR04(trigger_pin=18, echo_pin=5, echo_timeout_us=24000)
sensorLeft = HCSR04(trigger_pin=16, echo_pin=17, echo_timeout_us=24000)
sensorRight = HCSR04(trigger_pin=4, echo_pin=15, echo_timeout_us=24000)

NOTES = {
    "E5": 659,
    "G5": 784,
    "C5": 523,
    "D5": 587,
    "F5": 698,
    "REST": 0
}

melody = [("E5", 8)]

TEMPO = 40
WHOLE_NOTE = 60000 // TEMPO
DURATIONS = {
    1: WHOLE_NOTE,
    2: WHOLE_NOTE // 2,
    4: WHOLE_NOTE // 4,
    8: WHOLE_NOTE // 8,
    16: WHOLE_NOTE // 16
}

def play_note(note, duration):
    if note == "REST":
        buzzer.duty_u16(0)
    else:
        buzzer.freq(NOTES[note])
        buzzer.duty_u16(3000)
    sleep(duration / 1000)
    buzzer.duty_u16(0)
    sleep(0.01)

def blink_turn_signal(led, repetitions=3):
    for _ in range(repetitions):
        led.value(1)
        buzzer.duty(512)
        sleep(0.3)
        led.value(0)
        buzzer.duty(0)
        sleep(0.3)

def avanzar():
    in1.value(0)
    in2.value(1)
    enA.duty(1023)
    in3.value(0)
    in4.value(1)
    enB.duty(1023)
    ledYellow1.value(0)
    ledYellow2.value(0)

def retroceder():
    in1.value(1)
    in2.value(0)
    enA.duty(1023)
    in3.value(1)
    in4.value(0)
    enB.duty(1023)
    
    for _ in range(2):
        ledYellow1.value(1)
        ledYellow2.value(1)
        buzzer.duty(512)
        sleep(0.2)
        ledYellow1.value(0)
        ledYellow2.value(0)
        buzzer.duty(0)
        sleep(0.2)

def detener():
    in1.value(0)
    in2.value(0)
    enA.duty(1023)
    in3.value(0)
    in4.value(0)
    enB.duty(1023)

def mover_derecha():
    in1.value(0)
    in2.value(1)
    enA.duty(1023)
    in3.value(1)
    in4.value(0)
    enB.duty(1023)
    
    for _ in range(4.5):
        ledYellow1.value(1)
        buzzer.duty(512)
        sleep(0.3)
        ledYellow1.value(0)
        buzzer.duty(0)
        sleep(0.3)
    
    detener()

def mover_izquierda():
    in1.value(1)
    in2.value(0)
    enA.duty(1023)
    in3.value(0)
    in4.value(1)
    enB.duty(1023)
    
    for _ in range(4.5):
        ledYellow2.value(1)
        buzzer.duty(512)
        sleep(0.3)
        ledYellow2.value(0)
        buzzer.duty(0)
        sleep(0.3)
    
    detener()




def llegada_mensaje(topic, msg):
    if msg == b'5':
        ledRed.value(1)
        ledWhite.value(1)
    if msg == b'4':
        ledRed.value(0)
        ledWhite.value(0)
        


#Conectar a wifi
conectar_wifi()
#Subscripción a un broker mqtt
client = subscribir()


while True:
    
    client.wait_msg()
    
    distancia_front = sensorFront.distance_cm()
    distancia_back = sensorBack.distance_cm()
    distancia_left = sensorLeft.distance_cm()
    distancia_right = sensorRight.distance_cm()

    print('Distancia Frontal: ', distancia_front, 'cm')
    print('Distancia Trasera: ', distancia_back, 'cm')
    print('Distancia Derecha: ', distancia_right, 'cm')
    print('Distancia Izquierda: ', distancia_left, 'cm')
    
    if distancia_front > 40:
        avanzar()
    elif distancia_right > 40 and distancia_right >= distancia_left:
        mover_derecha()
    elif distancia_left > 40:
        mover_izquierda()
    elif distancia_back > 40:
        retroceder()
    else:
        detener()
        for note, duration in melody:
            play_note(note, DURATIONS[duration])
    
    sleep(0.1)
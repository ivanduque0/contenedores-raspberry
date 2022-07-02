import RPi.GPIO as GPIO
import time
import psycopg2
import os
import urllib.request

GPIO.cleanup()
# Tiempo de encendido
tiempo = 1 #Time interval in Seconds
total=0
pines=0
t2sensor=0
t1sensor=0
totalsensor=0
while True:
    conn = None
    # Se configuran los pines
    if pines==0:
        GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(7, GPIO.OUT)
        #GPIO.setup(5, GPIO.OUT)
        GPIO.setup(12, GPIO.IN)

        #GPIO.setup(26, GPIO.OUT)
        #buzzer=GPIO.PWM(26,700)

        GPIO.setwarnings(False)
        pines=1
    t1=time.perf_counter()
    while total<=5:
        t2=time.perf_counter()
        total=t2-t1
    try:
        conn = psycopg2.connect(
            database=os.environ.get("SQL_DATABASE"), user=os.environ.get("SQL_USER"), password=os.environ.get("SQL_PASSWORD"), host=os.environ.get("SQL_HOST"), port=os.environ.get("SQL_PORT")
        )
        conn.autocommit = False
        cursor = conn.cursor()

        while True:

            # cursor.execute('SELECT * FROM led WHERE acceso=%s', (os.environ.get("ACCESO"),))
            # led_onoff = cursor.fetchall()
            cursor.execute('SELECT * FROM sensor WHERE acceso=%s', (os.environ.get("ACCESO"),))
            sensor_onoff = cursor.fetchall() 
            #print(sensor_onoff)
            #print(totalsensor)
            if sensor_onoff[0][0] == 1:
                t2sensor=time.perf_counter()
            if t1sensor > 0:
                totalsensor=t2sensor-t1sensor
            if t1sensor == 0 and sensor_onoff[0][0] == 1:
                t1sensor=time.perf_counter()
            if GPIO.input(12) and sensor_onoff[0][0] == 0:
                #el acceso depende de cual puerta se vaya a aperturar
                cursor.execute('''UPDATE sensor SET onoff=1 WHERE acceso=%s;''', (os.environ.get("ACCESO"),))
                conn.commit()
                t1sensor=time.perf_counter()
            if GPIO.input(12) and sensor_onoff[0][0] == 1:
                t1sensor=time.perf_counter()
            if totalsensor > 10:
                cursor.execute('''UPDATE sensor SET onoff=0 WHERE acceso=%s;''', (os.environ.get("ACCESO"),))
                conn.commit()
                t1sensor=0
                t2sensor=0
                totalsensor=0


            #esto se usaba cuando la raspberry activaba la puerta ya sea con uno de los pines
            #o enviando una peticion al modulo wifi esp01

            # if led_onoff[0][0] == 1:
            #     #print("si reconocio")
            #     urllib.request.urlopen(os.environ.get("APERTURA_ON"))
            #     #GPIO.output(5, True)
            #     #buzzer.start(95)
            #     #time.sleep(0.2)
            #     #buzzer.stop()
            #     #time.sleep(0.1)
            #     #buzzer.start(95)
            #     #time.sleep(0.2)
            #     #buzzer.stop()
            #     #time.sleep(0.1)
            #     #buzzer.start(95)
            #     #time.sleep(0.2)
            #     #buzzer.stop()
            #     #time.sleep(0.1)
            #     #GPIO.output(5, False)
            #     #buzzer.stop()
            #     cursor.execute('''UPDATE led SET onoff=0 WHERE acceso=%s;''', (os.environ.get("ACCESO"),))
            #     conn.commit()

            # if led_onoff[0][0]==2:
            #     #print("no reconocio")
            #     urllib.request.urlopen(os.environ.get("APERTURA_OFF"))
            #     # GPIO.output(7, True)
            #     # buzzer.start(95)
            #     # time.sleep(tiempo)
            #     # buzzer.stop()
            #     # GPIO.output(7, False)
            #     cursor.execute('''UPDATE led SET onoff=0 WHERE acceso=%s;''', (os.environ.get("ACCESO"),))
            #     conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        total=0

    finally:
        print("se ha cerrado la conexion a la base de datos")
        if conn:
            cursor.close()
            conn.close()
            GPIO.cleanup()
            total=0
            pines=0

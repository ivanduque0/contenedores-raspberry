import RPi.GPIO as GPIO
import time
import psycopg2
import os

GPIO.cleanup()
# Tiempo de encendido
tiempo = 2 #Time interval in Seconds
total=0
pines=0
while True:
    conn = None
    # Se configuran los pines
    if pines==0:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)
        GPIO.setup(5, GPIO.OUT)
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
            cursor.execute('SELECT * FROM led')
            led_onoff = cursor.fetchall()

            if led_onoff[0][0] == 1:
                print("si reconocio")
                GPIO.output(5, True)
                time.sleep(tiempo)
                GPIO.output(5, False)
                cursor.execute('''UPDATE led SET onoff=0 WHERE onoff=1;''')
                conn.commit()

            if led_onoff[0][0]==2:
                print("no reconocio")
                GPIO.output(7, True)
                time.sleep(tiempo)
                GPIO.output(7, False)
                cursor.execute('''UPDATE led SET onoff=0 WHERE onoff=2;''')
                conn.commit()

    except (Exception, psycopg2.Error) as error:
        print("fallo en hacer las consultas")
        total=0

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("se ha cerrado la conexion a la base de datos")
            GPIO.cleanup()
            total=0
            pines=0

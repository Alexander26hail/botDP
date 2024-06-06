import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import schedule
import requests
from selenium.webdriver.chrome.options import Options
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dateutil.relativedelta import relativedelta
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json

# Función para crear el driver
def crear_driver():
    log_file = 'selenium.log'
    options = Options()
    #options.add_argument('--headless')  # modo headless (SIN VISTA)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
    
    return webdriver.Chrome(options=options)

def variablesData():
    with open('data.json', 'r') as archivo:
        data = json.load(archivo)
        return data

# VARIABLES
HoraInicio1 = "20:00"
HoraTermino1 = "21:00"
HoraInicio2 = "21:00"
HoraTermino2 = "22:00"
#webhook_url = "https://discord.com/api/webhooks/898800547816144907/lpmnykZHREjtvbTjGbKmBly6CujY7KbJec9OULOzSoTIeqNHWO62R394dSusDWXEIf66"
webhook_url = "https://discord.com/api/webhooks/1224428289951793244/qgUT4ZzRY4zUwy2xW4QtEZbs_nelsHBCjUqK3MwBxhLuse1LV-zIcbpNF8J40bWS3myi"
webhook_url_foto="https://discord.com/api/webhooks/1248133688969920553/xty_Hc681qUpf_RIxbH4w8YTj4Kv6M7XuJBZPvXqsmMdWNVK5W1PBgYZ9o3QWPNZZRNO"
HoraEjecucion1 = "00:01"
HoraEjecucion2 = "00:05"
gabriela = 2539
laurita = 2541
Reintento = 0
NombreRecinto = ''
RutSolicitud = ''
Filename="screenshot.png"

def URLFunc(Recinto, HoraInicio, HoraTermino):
    fecha_actual = datetime.now()
    siguiente_dia = fecha_actual + relativedelta(days=7)
    fecha_formateada = siguiente_dia.strftime("%d/%m/%Y")
    url = f"https://www.deportespuentealto.cl/recintos/{Recinto}/arrendar/0?tag_id=16&date={fecha_formateada}&range=60&start_time={HoraInicio}&end_time={HoraTermino}"
    
    return url

def FechaNacimiento(day, month, year, Reintento, driver):
    try:
        campo_day = driver.find_element('css selector', '[name="day"]')
        selectday = Select(campo_day)
        selectday.select_by_visible_text(day)
        campo_Month = driver.find_element('css selector', '[name="month"]')
        selectmonth = Select(campo_Month)
        selectmonth.select_by_value(month)

        campo_years = driver.find_element('css selector', '[name="year"]')
        campo_years.clear()
        campo_years.send_keys(year)
    except NoSuchElementException as e:
        if Reintento == 0:
            enviar_mensaje_discord("Gabriela no disponible")
            Reintento = 1
            job(laurita, Reintento, HoraInicio1, HoraTermino1)
            return
        else:
            enviar_mensaje_discord("Laurita no disponible!!! ALERTA")
            return "DataError: " + str(e)

def ReintentoRut(driver):
    global RutSolicitud
    item = random.choice(variablesData())
    
    run = item["run"]
    RutSolicitud= run
    day = item["birth_date"]["day"]
    month = item["birth_date"]["month"]
    year = item["birth_date"]["year"]

    try:
        campo_rut = driver.find_element('css selector', '[name="rut"]')
        campo_rut.clear()
        Runfunc(run, driver)
        FechaNacimiento(day, month, year, 0, driver)
        boton_siguiente = driver.find_element('css selector', '.btn.btn--primary.js-rentSubFormButton.js-complexFormButton.js-complexFormButton-Submit')
        boton_siguiente.click()
        elemento = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".messageBlock.alert")))
        if elemento:
            ReintentoRut(driver)
            print("MENSAJE YA TIENE RESERVA")
        
          
    except Exception as e:
        print(f"ENCONTRO EL RUT VALIDO")
        time.sleep(1)
def tomar_screenshot(driver, nombre_archivo):
    driver.save_screenshot(nombre_archivo)

def btnFinal(driver):
    global RutSolicitud
    try:
        boton_siguiente = driver.find_element('css selector', '.btn.btn--primary.js-rentSubFormButton.js-complexFormButton.js-complexFormButton-Submit')
        boton_siguiente.click()

        boton_confirmar = driver.find_element('css selector', '.btn.btn--primary.js-complexFormButton.js-complexFormButton-Submit')
        # Hacer clic en el botón "Confirmar"

        boton_confirmar.click()
        time.sleep(1)

        tomar_screenshot(driver,Filename)
        enviar_mensaje_discord_foto("Hora reservada",Filename)

        return "Succed:"
    except NoSuchElementException as e:
        return "DataError: " + str(e)

def Runfunc(run, driver):
    try:
        campo_rut = driver.find_element('css selector', '[name="rut"]')
        campo_rut.send_keys(run)
    except:
        enviar_mensaje_discord("NO HAY HORAS DISPONIBLES: " + RutSolicitud)

def enviar_mensaje_discord(mensaje):
    data = {
        "content": mensaje
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code != 204:
        print("Error al enviar el mensaje a Discord:", response.status_code)
def enviar_mensaje_discord_foto(mensaje, archivo_imagen=None):
    data = {
        "content": mensaje
    }

    if archivo_imagen:
        with open(archivo_imagen, 'rb') as f:
            files = {
                'file': (archivo_imagen, f)
            }
            response = requests.post(webhook_url_foto, data=data, files=files)
    else:
        response = requests.post(webhook_url, json=data)

    if response.status_code != 204:
        print("Error al enviar el mensaje a Discord:", response.status_code)

def job(Recinto,  HoraInicio, HoraTermino):
    global RutSolicitud
    try:
        url = URLFunc(Recinto, HoraInicio, HoraTermino)
        driver = crear_driver()
        driver.get(url)
        boton_siguiente = driver.find_element('css selector', '.btn.btn--primary.js-complexFormButton.js-complexFormButton-Submit')
        boton_siguiente.click()

        ReintentoRut(driver)
        btnResult = btnFinal(driver)
        if btnResult.startswith("DataError"):
            return
        else:
            if Recinto == 2539:
                NombreRecinto = 'Gabriela'
            else:
                NombreRecinto = 'Laurita'

            enviar_mensaje_discord("Hora reservada para el RUT : " + RutSolicitud + " Hora: " + HoraInicio + "=" + HoraTermino + "-Recinto:" + NombreRecinto)
            driver.quit()
    except Exception as e:
        enviar_mensaje_discord("Error al ejecutar BOOT PUENTE ALTO RUT: " + RutSolicitud + " Hora: " + HoraInicio + "=" + HoraTermino + " Mensaje error: " + str(e) + " Recinto: " + str(Recinto))

# Programación de tareas
try:
    
    schedule.every().friday.at(HoraEjecucion1).do(lambda: job(gabriela, HoraInicio1,HoraTermino1))
    schedule.every().friday.at(HoraEjecucion2).do(lambda: job(gabriela, HoraInicio2,HoraTermino2))
    schedule.every().wednesday.at(HoraEjecucion1).do(lambda: job(gabriela, "19:00","20:00"))
    schedule.every().wednesday.at(HoraEjecucion2).do(lambda: job(gabriela, HoraInicio1,HoraTermino1))
    #job(gabriela, HoraInicio2, HoraTermino2)
    while True:
        schedule.run_pending()
        time.sleep(1)
except Exception as e:
    enviar_mensaje_discord("Error al ejecutar BOOT PUENTE ALTO: " + str(e))

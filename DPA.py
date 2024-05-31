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
from selenium.common.exceptions import NoSuchElementException , TimeoutException
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
webhook_url = "https://discord.com/api/webhooks/1224428289951793244/qgUT4ZzRY4zUwy2xW4QtEZbs_nelsHBCjUqK3MwBxhLuse1LV-zIcbpNF8J"
HoraEjecucion1 = "00:01"
HoraEjecucion2 = "00:05"
gabriela = 2539
laurita = 2541
Reintento = 0
NombreRecinto = ''
RutSolicitud=''

def URLFunc(Recinto,HoraInicio , HoraTermino):
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
            job(laurita, Reintento)
            return
        else:
            enviar_mensaje_discord("Laurita no disponible!!! ALERTA")
            return "DataError: " + str(e)

def ReintentoRut(driver):
    item= random.choice(variablesData())
    
    run = item["run"]
    RutSolicitud=run
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
        # Verificar si tiene una reserva
        if elemento:
            ReintentoRut(driver)
            print("MENSAJE YA TIENE RESERVA")
    except Exception as e:
        print(f"ENCONTRO EL RUT VALIDO")
        time.sleep(1)

def btnFinal(driver):
    try:
        boton_siguiente = driver.find_element('css selector', '.btn.btn--primary.js-rentSubFormButton.js-complexFormButton.js-complexFormButton-Submit')
        boton_siguiente.click()

        ReintentoRut(driver)

        boton_siguiente = driver.find_element('css selector', '.btn.btn--primary.js-rentSubFormButton.js-complexFormButton.js-complexFormButton-Submit')
        boton_siguiente.click()

        boton_confirmar = driver.find_element('css selector', '.btn.btn--primary.js-complexFormButton.js-complexFormButton-Submit')

        # Hacer clic en el botón "Confirmar"
        #boton_confirmar.click()
        return "Succed:"
    except NoSuchElementException as e:
        return "DataError: " + str(e)

def Runfunc(run, driver):
    try:
        campo_rut = driver.find_element('css selector', '[name="rut"]')
        campo_rut.send_keys(run)
    except:
        enviar_mensaje_discord("NO HAY HORAS DISPONIBLES: "+RutSolicitud)

def enviar_mensaje_discord(mensaje):
    data = {
        "content": mensaje
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code != 204:
        print("Error al enviar el mensaje a Discord:", response.status_code)


def job(Recinto, Reintento,HoraInicio,HoraTermino):
    try:
        url = URLFunc(Recinto,HoraInicio,HoraTermino)
        # Crear el driver al inicio
        driver = crear_driver()
        driver.get(url)
        boton_siguiente = driver.find_element('css selector', '.btn.btn--primary.js-complexFormButton.js-complexFormButton-Submit')
        boton_siguiente.click()

        # Seleccionar un objeto aleatorio del JSON
        item = random.choice(variablesData())
        run = item["run"]
        RutSolicitud= run
        day = item["birth_date"]["day"]
        month = item["birth_date"]["month"]
        year = item["birth_date"]["year"]

        Runfunc(run, driver)
        FechaNacimiento(day, month, year, Reintento, driver)
        btnResult = btnFinal(driver)
        if btnResult.startswith("DataError"):
            return
        else:
            if Recinto == 2539:
                NombreRecinto = 'Gabiela'
            else:
                NombreRecinto = 'Laurita'

            enviar_mensaje_discord("Hora reservada para el RUT : " + RutSolicitud + " Hora: " + HoraInicio + "=" + HoraTermino + "-Recinto:" + NombreRecinto)
            # Cerrar el navegador
            driver.quit()
    except:
        enviar_mensaje_discord("Error al ejecutar BOOT PUENTE ALTO RUT: "+RutSolicitud+" Hora: "+ HoraInicio +"="+ HoraTermino +" Mensaje error"+ "Recinto " + Recinto)

# Programación de tareas
try:

    #schedule.every().friday.at(HoraEjecucion1).do(lambda: job(gabriela, 0,HoraInicio1,HoraTermino1))
    #schedule.every().friday.at(HoraEjecucion2).do(lambda: job(gabriela, 0,HoraInicio2,HoraTermino2))
    #schedule.every().wednesday.at(HoraEjecucion1).do(lambda: job(gabriela, 0,"19:00","20:00"))
    #schedule.every().wednesday.at(HoraEjecucion2).do(lambda: job(gabriela, 0,HoraInicio1,HoraTermino1))

    job(gabriela, 0,"20:00","21:00")
    #schedule.every().monday.at('04:39:00').do(lambda: job(gabriela, 0,HoraInicio1,HoraTermino1))
    #schedule.every().monday.at('04:40:00').do(lambda: job(gabriela, 0,HoraInicio1,HoraTermino1))


    

except Exception as e:
    # Manejo de excepciones
    enviar_mensaje_discord("Error al ejecutar BOOT PUENTE ALTO : "+e)


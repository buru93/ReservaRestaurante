from os import path
from bs4.element import whitespace_re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
    
check = True

def checkMove(element):
    """Funcion para comprobar si el boton de avance en el calendario esta disponible"""
    htmlClass = element.get_attribute("class")
    if "ui-state-disabled" not in htmlClass:
        return True
    else:
        return False


def getDataMonth(elementPage):
    """Funcion que recibe el mes y obtiene las clases de cada fila del mes"""
    data = []
    # BeautifulSoup del HTML del calendario
    tableMonth = BeautifulSoup(elementPage.query_selector("table.ui-datepicker-calendar > tbody").inner_html(), features='html.parser')
    for tr in tableMonth.find_all("td"):
        # Se usa isinstance porque cuando no hay clase por los dias pasados es NoneType
        if isinstance(tr.get("data-month"),type(None)) != True:
            temp = (tr.getText(), tr.get("data-month"), tr.get("class"))
        else:
            temp = (tr.getText(), 0, tr.get("class"))
        data.append(temp)
        del temp
    return data

def freeDays(data):
    """Funcion que recibe list y selecciona todos los dias disponibles para devolver lista con los dias dispo y su mes"""
    listFreeDays = []
    week = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    for tup in data:
        if "complete" not in tup[2] and "closec" not in tup[2]:
            listFreeDays.append("El dia " + tup[0] + " de " + week[int(tup[1])] + " esta libre para reservar")
    
    return listFreeDays


with sync_playwright() as p:
    # Se crear navegador, se lanza y accede a pagina
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.grupomontoro.es/espacio/reservas/')

    # Al ser una pagina con iframes, para poder navegar y scrapear hay que entrar en ellos
    # Definimos el donde se encuentra el calendario
    frame_one = page.wait_for_selector('#iFrameResizer0').content_frame()
    # Dentro del frame ya podemos navegar por el html asi que buscamos el calendario pequeno
    divCalendar = frame_one.wait_for_selector(".contenedor_small_calendar")
    divCalendar.scroll_into_view_if_needed()
    # tomarFoto(divCalendar)
    iconCalendar = divCalendar.wait_for_selector(".more")
    iconCalendar.click()
    # Seleccionamos el calendario grande
    bigCalendar = frame_one.wait_for_selector("#datepicker_calendar")

    
    while check == True:
        data = getDataMonth(bigCalendar)
        days = []

        if len(freeDays(data)) != 0:
            days.append(freeDays(data))
        
        # Coge los datos del calendario actual
        nextMonth = bigCalendar.wait_for_selector(".ui-datepicker-next")
        # Antes de hacer click en el boton de cambiar mes comprobamos estado para ver si es posible seguir avanzando
        check = checkMove(nextMonth)
        if check == True:
            # Actualizacion de los datos al cambiar de pagina
            nextMonth.click()
    
    if len(days) != 0:
        print(days)
    else: 
        print("No hay ninguna fecha disponible")


    browser.close()
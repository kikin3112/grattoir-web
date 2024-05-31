import undetected_chromedriver as uc
import pyautogui
import time
import os
import pyperclip
import shutil
from bs4 import BeautifulSoup as bs
import pandas as pd

#Columnas con información específica no raspada
edx = 'EDX'
metodologia = 'MOOC (xMOOC)'
certificacion = 'Disponible'

options = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=options)

#Directorios de ubicaciones a tener en cuenta.
descargas_default = r'C:\Users\luisr\Downloads'
destino_resultados = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Edx\resultados'
destino_cursos = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Edx\cursos'

def sensor(origen, nombre_archivo, destino):
        """
        Comprueba si el nombre_archivo.html ya se descargó y lo mueve del origen
        al destino.
        """
        descarga = os.path.join(origen, nombre_archivo + '.html')
        if os.path.exists(descarga):
            shutil.move(descarga, destino)
            return True
        else:
            return False
        
#Almacena los nombres de los archivos.html de cada RESULTADO,
#para luego acceder a ellos y extraer links, nombres, niveles y
#duraciones de cada curso.
html_resultados = []

for i in range(1, 4): #especifica el número de páginas con resultados a obtener.
    url = 'https://www.edx.org/search?q=marketing+digital&tab=course&page=' + str(i) + '&learning_type=Course'
    driver.get(url)

    pyautogui.press('esc')
    time.sleep(5)
    pyautogui.hotkey('ctrl','s')
    time.sleep(2)
    pyautogui.press('right')
    pyautogui.press('_')
    pyautogui.press(str(i))
    time.sleep(1)
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('ctrl','c')
    pyautogui.press('enter')
    nombre_resultados = pyperclip.paste()

    while not sensor(descargas_default, nombre_resultados, destino_resultados):
        time.sleep(1)

    html_resultados.append(nombre_resultados)

# Extracción de link, nombre y encargado de cada curso
# (se extraen primeramente los links para poder acceder y 
# descargar los .html con el resto de información de cada curso).
link = []
nombre = []
encargado = []

for r in html_resultados:
    sopa_resultado = bs(open(os.path.join(destino_resultados, r + '.html'), 'r'), 'html.parser')
    links = sopa_resultado.find_all('a', class_ = 'base-card-link')
    for l in links:
        link.append(l.get('href'))
    cursos = sopa_resultado.find_all('div', class_ = 'pgn__card-header-title-md')
    for c in cursos:
        titulo = ' '.join(c.stripped_strings)
        nombre.append(titulo[:-1])
    encargados = sopa_resultado.find_all('div', class_ = 'pgn__card-header-subtitle-md')
    for e in encargados:
         host = ' '.join(e.stripped_strings)
         encargado.append(host[:-1])

#Almacena los nombres de los archivos.html de cada CURSO,
#para luego acceder a ellos y extraer...
html_cursos = []

for l in link:
    url = str(l)
    driver.get(url)

    pyautogui.press('esc')
    time.sleep(5)
    pyautogui.hotkey('ctrl','s')
    time.sleep(2)
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('ctrl','c')
    pyautogui.press('enter')
    nombre_cursos = pyperclip.paste()
    
    while not sensor(descargas_default, nombre_cursos, destino_cursos):
        time.sleep(1)

    html_cursos.append(nombre_cursos)
    time.sleep(1)

driver.quit()

# Extracción de descripción, contenido, duración,
# idioma, nivel y precio de cada curso.
descripcion = []
contenido = []
duracion = []
idioma = []
nivel = []
precio = []
inscrito = []

for n in html_cursos:
    sopa_curso = bs(open(os.path.join(destino_cursos, n + '.html'), 'r'), 'html.parser')

    box_description = sopa_curso.find('div', class_='mt-2 lead-sm html-data')
    box_content = sopa_curso.find_all('div', class_ = 'mt-2 html-data')
    box_time = sopa_curso.find('div', class_ = 'd-flex align-items-start col-12 pb-4 pb-md-0 col-md-4')
    box_lang = sopa_curso.find('ul', class_ = 'pl-3 ml-1 mb-0')
    box_level = sopa_curso.find('ul', class_ = 'mb-0 pl-3 ml-1')
    box_price = sopa_curso.find('table', class_ = 'track-comparison-table m-md-auto')
    box_enroled = sopa_curso.find('div', class_ = 'course-selection mt-md-4 container-mw-lg container-fluid')

    descripciones = box_description.get_text()
    descripcion.append(descripciones)
    if box_content:
        contenidos = box_content[0].get_text()
        contenido.append(contenidos)
    else:
        contenido.append('Información no disponible')
    tiempos = box_time.find('div', class_ = 'h4 mb-0').get_text()
    duracion.append(tiempos)
    language = box_lang.find('li').get_text().split(': ')
    if len(language) > 1:
        idioma.append(language[1])
    else:
        idioma.append('REVISAR')
    level = box_level.find_all('li')
    niveles = (level[2].get_text().split(': '))[1]
    nivel.append(niveles)
    if box_price is not None:
        price_tags = box_price.find_all('p')
        if price_tags:
            price = price_tags[0].get_text()
        else:
            price = 'Información no disponible'
    else:
        price = 'Información no disponible'
    precio.append(price)
    enrolado = box_enroled.find('div', class_ = 'small')
    if enrolado is not None:
        inscritos = enrolado.text.split(' ')[0]
        if 'After' in inscritos:
            inscritos = 'Información no disponible'
    else:
        inscritos = 'Información no disponible'
    inscrito.append(inscritos)

#Creación de base de datos con la información raspada.

df = pd.DataFrame({'Plataforma': edx,
                   'URL del curso': link,
                   'Nombre del curso': nombre,
                   'Encargado/s del curso': encargado,
                   'Idioma del curso': idioma,
                   'Descripción del curso': descripcion,
                   'Contenido del curso': contenido,
                   'Metodología del curso': metodologia,
                   'Nivel del curso': nivel,
                   'Duración del curso': duracion,
                   'Precio del curso': precio,
                   'Certificación': certificacion,
                   'Inscritos en el curso': inscrito
                   })


#df.to_csv('bm_edx.csv', sep=';', encoding='utf-8-sig')
df.head()
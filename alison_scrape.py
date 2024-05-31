import undetected_chromedriver as uc
import pyautogui
import time
import os
import pyperclip
import shutil
from bs4 import BeautifulSoup as bs
import pandas as pd

#Columnas con información específica no raspada
alison = 'ALISON'
metodologia = 'MOOC (xMOOC)'
certificacion = 'Disponible'
precio = 'Gratis'
idioma = 'Inglés'
nivel = 'Todos los niveles'

options = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=options)

#Directorios de ubicaciones a tener en cuenta.
descargas_default = r'C:\Users\luisr\Downloads'
destino_resultados = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Alison\resultados'
destino_cursos = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Alison\cursos'

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

for i in range(6, 11): #especifica el número de páginas con resultados a obtener.
    url = 'https://alison.com/courses?language=en&query=marketing%20digital&page=' + str(i)
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

# Extracción de link, nombre, duración e inscrito de cada curso
# (se extraen primeramente los links para poder acceder y 
# descargar los .html con el resto de información de cada curso).
link = []
nombre = []
duracion = []
inscrito = []

for r in html_resultados:
    sopa_resultado = bs(open(os.path.join(destino_resultados, r + '.html'), 'r'), 'html.parser')
    cursos = sopa_resultado.find('ul', class_ = 'course-listing clearfix')

    links = cursos.find_all('a', class_ ='card__more card__more--mobile')
    for l in links:
        link.append(l.get('href'))
    nombres = cursos.find_all('h3')
    for n in nombres:
        clean_nombre = n.get_text()
        nombre.append(clean_nombre)
    times = cursos.find_all('span', class_ = 'card__duration')
    for t in times:
        clean_time = t.get_text()
        duracion.append(clean_time)
    enroled = cursos.find_all('span', class_ = 'card__enrolled')
    for e in enroled:
        clean_e =  e.get_text().split(' ')[0]
        inscrito.append(clean_e)

#Almacena los nombres de los archivos.html de cada CURSO,
#para luego acceder a ellos y extraer...
html_cursos = []

n = 0
for l in link:
    url = str(l)
    driver.get(url)

    pyautogui.press('esc')
    time.sleep(5)
    pyautogui.hotkey('ctrl','s')
    time.sleep(2)
    pyautogui.press('right')
    pyautogui.press('_')
    pyautogui.typewrite(str(n))
    n += 1
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
encargado = []

for n in html_cursos:
    sopa_curso = bs(open(os.path.join(destino_cursos, n + '.html'), 'r'), 'html.parser')

    box_content = sopa_curso.find('div', class_ = 'l-mods course-modules')
    box_description = sopa_curso.find('div', class_ = 'l-desc course-desc')
    box_host = sopa_curso.find('span', class_ = 'course-publisher')

    #CONTENIDO (Nombre módulo)

    titulo_contenido = []
    titulo = box_content.find_all('h3')
    cont_b_pp = []
    for t in titulo:
        cont_b_pp.append(t.text)
    titulo_contenido.append(cont_b_pp)

    #CONTENIDO (Descripción módulo)

    items_contenido = []
    topic = box_content.find_all('div',class_ = 'l-mods__topics')
    cont_desc_pp = []
    for t in topic:
        cont_desc_pp.append(t.text)
    items_contenido.append(cont_desc_pp)

    #CONTENIDO (Nombre + descripción)

    pre_contenido = [[f"{x}: {y}\n" for x, y in zip(sub_a, sub_b)] for sub_a, sub_b in zip(titulo_contenido, items_contenido)]
    contenido.append(pre_contenido[0])

    descripciones = box_description.get_text()
    descripcion.append(descripciones)

    host = box_host.text
    encargado.append(host)

#Creación de base de datos con la información raspada.

df = pd.DataFrame({'Plataforma': alison,
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

# df.to_csv('bm_alison_200.csv', sep=';', encoding='utf-8-sig')
df.head()
# Extracción: 28 de abril del 2024, 4:20 p.m.
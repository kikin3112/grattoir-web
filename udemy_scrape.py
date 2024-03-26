import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pyautogui
import time
import os
import pyperclip
import shutil
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

#Columnas con información específica no raspada
udemy = 'UDEMY'
modalidad = 'Course'
metodologia = 'MOOC (xMOOC)'
certificacion = 'Available'

options = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=options)

#Directorios de ubicaciones a tener en cuenta.
descargas_default = r'C:\Users\luisr\Downloads'
destino_resultados = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Udemy\pw_resultados'
destino_cursos = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Udemy\pw_cursos'

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

for i in range(1, 2): #especifica el número de páginas con resultados a obtener.
    url = 'https://www.udemy.com/courses/search/?lang=en&lang=es&p=' + str(i) + '&q=marketing+digital&sort=relevance&src=ukw'
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
    
    while not sensor(descargas_default, nombre_resultados, destino_resultados):
        time.sleep(1)

    nombre_resultados = pyperclip.paste()
    html_resultados.append(nombre_resultados)
    
# Extracción de link, nombre, nivel y duración de cada curso
# (se extraen primeramente los links para poder acceder y 
# descargar los .html con el resto de información de cada curso).
link = []
nombre = []
nivel = []
duracion = []

for r in html_resultados:
    sopa_resultado = bs(open(os.path.join(destino_resultados, r + '.html'), 'r'), 'html.parser')
    cursos = sopa_resultado.find('div', class_ = 'course-list--container--HY2ry')
    div_borrador = cursos.find_all('div', class_ = 'search--unit-injection--CZ1Sp')
    for div_borrado in div_borrador:
        div_borrado.decompose()
        
    titulo_curso = cursos.find_all('h3', class_='ud-heading-md course-card-title-module--course-title--wmFXN')
    for n in titulo_curso:
        links = n.a.get('href')
        link.append(links) #clean_link
        textos = n.find_all('a')
        for t in textos:
            n = ''
            for i in t.contents:
                if not getattr(i, 'name', None) == 'div': #excluir div
                    n += str(i)
            n = n.strip()
            nombre.append(n) #clean_nombre

    detalles_curso = cursos.find_all('div', class_ = 'course-card-module--main-content--pEiUr course-card-module--has-price-text--g6p85')
    for c in detalles_curso:
        detalle = c.find_all('span', class_ = 'course-card-details-module--row--jw-lD')
        n = detalle[2].get_text(strip=True)
        nivel.append(n)
        t = detalle[0].get_text(strip=True)
        duracion.append(t)

#Almacena los nombres de los archivos.html de cada CURSO,
#para luego acceder a ellos y extraer...
html_cursos = []

for l in link:
    url = str(l)
    driver.get(url)

    pyautogui.press('esc')
    time.sleep(5)

    try: #muestra todo el contenido
        todo_contenido = driver.find_element(By.CLASS_NAME, 'ud-btn.ud-btn-medium.ud-btn-secondary.ud-heading-sm.curriculum--curriculum-show-more--hf-k5')
        todo_contenido.click()
    except NoSuchElementException:
        pass

    pyautogui.hotkey('ctrl','s')
    time.sleep(2)
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('ctrl','c')
    pyautogui.press('enter')

    while not sensor(descargas_default, nombre_cursos, destino_cursos):
        time.sleep(1)

    nombre_cursos = pyperclip.paste()
    html_cursos.append(nombre_cursos)
    time.sleep(1)

driver.quit()

#Extracción de idioma, precio, descipción,
#contenido y encargado.

idioma = []
precio = []
descripcion = []
clean_contenidos = []
encargado = []

for n in html_cursos:

    sopa_curso = bs(open(os.path.join(destino_cursos, n + '.html'), 'r'), 'html.parser')

    box_lang = sopa_curso.find('div', class_='clp-lead__element-item clp-lead__locale')
    box_price = sopa_curso.find('div', class_='base-price-text-module--container--Sfv-5 ud-clp-price-text')
    box_description = sopa_curso.find('div', class_ = 'ud-text-sm component-margin styles--description--AfVWV')
    box_content = sopa_curso.find_all('div', class_ = 'accordion-panel-module--panel--Eb0it section--panel--qYPjj')
    box_host = sopa_curso.find('span', class_ = 'instructor-links--names--fJWai')

    lang = box_lang.get_text()
    idioma.append(lang) #clean_idioma

    span = box_price.find_all('span')
    precios = span[1]
    for p in precios:
        n = p.get_text(strip=True)
        clean_price = re.sub(r'\D', '', n) #precio cleaner
        precio.append(clean_price) #clean_precio

    descripciones = box_description.find('div', class_='show-more-module--content--Rw-xr show-more-module--with-gradient--f4HoJ')
    parrafos = descripciones.find_all('p')
    texto = []
    for p in parrafos:
        texto.append(p.get_text(separator=' ', strip=True))
    texto_formateado = '\n'.join(texto)
    descripcion.append(texto_formateado) #clean_descripcion

    instructor = box_host.find_all('a')
    nombres_instructor = []
    for i in instructor:
        n = i.get_text(strip=True)
        if '•' in n:
            n = n.split('•')[0].strip()
        nombres_instructor.append(n)    
    encargado.append(nombres_instructor) #clean_encargado

    #CONTENIDO (Nombre módulo)

    titulo_contenido = []
    for c in box_content:
        contenidos = c.find('span', class_ = 'section--section-title--svpHP')
        cont_b_pp = []
        for c in contenidos:
            n = c.get_text(strip=True)
            cont_b_pp.append(n)
        titulo_contenido.append(cont_b_pp)

    #CONTENIDO (Descripción módulo)
        
    items_contenido = []
    for c in box_content:
        contenidos_desc = c.find_all('div', class_ = "section--row--MuPRa")
        cont_desc_pp = []
        for d in contenidos_desc:
            n = d.get_text(strip=True)
            cont_desc_pp.append(n)
        items_contenido.append(cont_desc_pp)

    #CONTENIDO (Nombre + descripción)
        
    pre_contenido = []
    contenido = []
    for breve, full in zip(titulo_contenido, items_contenido):
        combinado = "{}: ".format(breve[0])
        for i, num in enumerate(full):
            if i == len(full) - 1:
                combinado += "{}.".format(num)
            else:
                combinado += "{} - ".format(num)
        pre_contenido.append(combinado)
        result = '\n\n'.join(pre_contenido)
    contenido.append(result)
    clean_contenidos.extend(contenido)

#Creación de base de datos con la información raspada.

df = pd.DataFrame({'Plataforma': udemy,
                   'Modalidad': modalidad,
                   'URL del curso': link,
                   'Nombre del curso': nombre,
                   'Encargado/s del curso': encargado,
                   'Idioma del curso': idioma,
                   'Descripción del curso': descripcion,
                   'Contenido del curso': clean_contenidos,
                   'Metodología del curso': metodologia,
                   'Nivel del curso': nivel,
                   'Duración del curso': duracion,
                   'Precio del curso': precio,
                   'Certificación': certificacion
                   })

df.head()
#df.to_csv('bm_udemy.csv', sep=';', encoding='utf-8-sig')
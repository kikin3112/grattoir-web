import undetected_chromedriver as uc
import pyautogui
import time
import os
import pyperclip
import shutil
from bs4 import BeautifulSoup as bs
import pandas as pd

#Columnas con información específica no raspada
domestika = 'DOMESTIKA'
metodologia = 'MOOC (xMOOC)'
certificacion = 'Disponible'
precio = '156000'

# Extracción de link, nombre, duración e inscrito de cada curso
# (se extraen primeramente los links para poder acceder y 
# descargar los .html con el resto de información de cada curso).
link = []
nombre = []
encargado = []
inscrito = []

html_resultado = 'Los mejores cursos online de marketing digital _ Actualizado en 2024 _ Domestika.html'

with open(html_resultado, 'r') as file:
    sopa_resultado = bs(file, 'html.parser')
    cursos = sopa_resultado.find('div', class_ = 'Grid d:grid gtc-1 ai:inherit sm$gtc-2 md$gtc-3 lg$gtc-4 rowg-s sm$rowg-s md$rowg-s lg$rowg-s colmg-m sm$colmg-l md$colmg-l lg$colmg-l undefined')

    links = cursos.find_all('div', class_ = 'ContanierCard-TitleContainer mb-xs')
    for l in links:
        link.append(l.find('a')['href'])
    nombres = cursos.find_all('h3')
    for n in nombres:
        clean_nombre = n.get_text()
        nombre.append(clean_nombre)
    encargados = cursos.find_all('div', class_ = 'Typography(SRegular) fz-s lh-l lts-m fw-regular ff-inter sm$fz-s sm$lh-l sm$lts-m sm$fw-regular sm$ff-inter md$fz-s md$lh-l md$lts-m md$fw-regular md$ff-inter lg$fz-s lg$lh-l lg$lts-m lg$fw-regular lg$ff-inter ContanierCard-TeacherClass d:-webkit-box lc-1 ov:hidden bxo:vertical')
    for e in encargados:
        clean_encargados = e.get_text()
        encargado.append(clean_encargados)
    inscritos = cursos.find_all('span', class_ = 'Typography(SRegular) fz-s lh-l lts-m fw-regular ff-inter sm$fz-s sm$lh-l sm$lts-m sm$fw-regular sm$ff-inter md$fz-s md$lh-l md$lts-m md$fw-regular md$ff-inter lg$fz-s lg$lh-l lg$lts-m lg$fw-regular lg$ff-inter ContanierCard-StudentsClass ml-2xs c-neutral-800')
    for i in inscritos:
        clean_inscritos = i.get_text()
        inscrito.append(clean_inscritos)

options = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=options)

#Directorios de ubicaciones a tener en cuenta.
descargas_default = r'C:\Users\luisr\Downloads'
destino_cursos = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Domestika\cursos'

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
idioma = []
contenido = []
nivel = []
duracion = []

for n in html_cursos:
    sopa_curso = bs(open(os.path.join(destino_cursos, n + '.html'), 'r'), 'html.parser')

    box_course = sopa_curso.find('div', class_ = 'course-page__content course-page__content--with-sidebar js-course-page-content')
    box_caracteristicas = box_course.find('div', class_ = 'grid grid-cols-2 gap-l')
    box_content = box_course.find('div', class_ = 'toc-new')

    descripcion_titulo = box_course.find('h2', class_ = 'course-header-new__short-description d-none d-md-block')
    descripcion_texto = box_course.find('div', class_ = 'js-content w-full h-full overflow-hidden')

    descripcion_full = descripcion_titulo.get_text() + descripcion_texto.get_text()
    if descripcion_full[0] == '\n' and descripcion_full[-1] == "\n":
        descripcion.append(descripcion_full[1:-1])
    else:
        descripcion.append(descripcion_full) #clean_descripcion

    idiomas = box_caracteristicas.find_all('li', class_ = 'flex gap-xs')
    for i in idiomas:
        n = i.get_text()
        if 'Audio' in n:
            clean_i = n.replace('\n', '')
            clean_i = clean_i.replace('Audio: ', '')
            idioma.append(clean_i) #clean_idioma

    niveles = box_caracteristicas.find_all('li', class_ = 'flex gap-xs')
    for i in niveles:
        n = i.get_text()
        if 'Nivel' in n:
            clean_n = n.replace('\n', '')
            clean_n = clean_n.replace('Nivel: ', '')
            nivel.append(clean_n) #clean_nivel

    tiempos = box_caracteristicas.find_all('li', class_ = 'flex gap-xs')
    for i in tiempos:
        n = i.get_text()
        if 'lecciones' in n:
            clean_t = n.replace('\n', '')
            duracion.append(clean_t) #clean_duracion

    #CONTENIDO (Nombre módulo)

    titulo_contenido = []
    titulo = box_content.find_all('h4', class_ = 'media-body toc-new__unit-title')
    for t in titulo:
        cont_b_pp = []
        n = t.get_text()
        clean_titulo = n.replace('\n', '')
        cont_b_pp.append(clean_titulo)
        titulo_contenido.append(cont_b_pp)

    #CONTENIDO (Descripción módulo)

    items_contenido = []
    items = []
    topic = box_content.find_all("li", class_ = 'toc-new__item')
    for t in topic:
        topics = t.find_all('ul', class_ = 'toc-new__lessons-list')
        for t in topics:
            n = t.get_text()
            items.append(n)
    for sublist in items:
        cont_desc_pp = []
        for element in sublist.split('\n'):
            if element.strip():
                cont_desc_pp.append(element.strip())
        items_contenido.append(cont_desc_pp)

    # CONTENIDO (Nombre + descripción)

    a = titulo_contenido
    b = items_contenido
    c = []
    for num, items in zip(a, b):
        formatted_string = f"{num[0]}: {' - '.join(items)}\n\n"
        c.append(formatted_string)
    contenido.append(c) #clean_contenido

df = pd.DataFrame({'Plataforma': domestika,
                   'URL del curso': link,
                   'Nombre del curso': nombre,
                   'Encargado/s del curso': encargado,
                   'Inscripciones en el curso': inscrito,
                   'Idioma del curso': idioma,
                   'Descripción del curso': descripcion,
                   'Contenido del curso': contenido,
                   'Metodología del curso': metodologia,
                   'Nivel del curso': nivel,
                   'Duración del curso': duracion,
                   'Precio del curso': precio,
                   'Certificación': certificacion
                   })


#df.to_csv('bm_domestika.csv', sep=';', encoding='utf-8-sig')
df.head()
# Extracción: 27 de abril del 2024, 7:01 p.m.
from bs4 import BeautifulSoup
import requests
import pandas as pd

coursera = 'COURSERA'
link = []
#modalidad = []
nombre = []
encargado = []
idioma = []
descripcion = []
#contenido = []
metodologia = 'MOOC (xMOOC)'
nivel = []
duracion = []
precio = []
certificacion = 'Available'

for i in range(1, 2):

    pw = 'https://www.coursera.org/search?query=marketing%20digital&topic=Business&language=English&language=Spanish&productTypeDescription=Courses&page='+ str(i) +'&sortBy=BEST_MATCH&irclickid=TgIwQOWrzxyPWxCVA-3CCUm4UkHygdQ3MTz02w0&irgwc=1&utm_medium=partners&utm_source=impact&utm_campaign=3306008&utm_content=b2c'
    r = requests.get(pw)
    soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')

    ctrl_precio = []
    catalogo = soup.find_all('li', class_='cds-9 css-0 cds-11 cds-grid-item cds-56 cds-64 cds-76 cds-90')
    for curso in catalogo:
        etiquetas = []
        for etiqueta in curso.find_all('span', class_='css-1rlln5c'):
            etiquetas.append(etiqueta.get_text())
        ctrl_precio.append(etiquetas)
    for label in ctrl_precio:
        if label == ['New']:
            precio.append('Paid')
        elif label == ['Free']:
            precio.append('Free')
        elif label == ['New', 'Free']:
            precio.append(label[1])
        else:
            precio.append('Paid')

    nombres = soup.find_all('h3', class_ = 'cds-CommonCard-title css-6ecy9b')
    for i in nombres:
        n = i.get_text(strip=True).encode('latin-1').decode('utf-8')
        nombre.append(n)

    encargados = soup.find_all('div', class_ = 'css-cxybwo cds-ProductCard-partners')
    for i in encargados:
        n = i.get_text(strip=True).encode('latin-1').decode('utf-8')
        encargado.append(n[1:])

    links = soup.find_all('a', class_ = 'cds-119 cds-113 cds-115 cds-CommonCard-titleLink css-si869u cds-142')
    for i in links:   
        n = 'https://www.coursera.org' + i.get('href')
        link.append(n)

    clasificacion = soup.find_all('div', class_ = 'cds-CommonCard-metadata')
    for i in clasificacion:
        tiempo_duracion = i.find_all('p', class_ = 'css-vac8rf')
        n = i.get_text(strip=True).encode('latin-1').decode('utf-8')
        n = n.split('·')
        nivel.append(n[0])
        duracion.append(n[2])

for l in link:
    r_pw_enter = requests.get(l)
    sopa_pw_enter = BeautifulSoup(r_pw_enter.text, 'html.parser', from_encoding='utf-8')

    box_lang = sopa_pw_enter.find_all('div', class_ = 'css-ddn3zj')
    box_description = sopa_pw_enter.find_all('div', class_ = 'css-1m8ahwj')
    box_content = sopa_pw_enter.find_all('div', class_ = 'css-1i4o2ol')

    #IDIOMAS

    for l in box_lang:
        idiomas = l.find_all('p', class_ = 'css-4s48ix')
        for i in idiomas:
            n = i.get_text(strip=True).encode('latin-1').decode('utf-8')
            idioma.append(n)

    #DESCRIPCIONES

    for d in box_description:
        descripciones = d.find_all('p', class_ = False)
        if len(descripciones) == 0:
            pass
        elif len(descripciones) == 1:
            for d in descripciones:
                n = d.get_text(strip=True).encode('latin-1').decode('utf-8')
                descripcion.append(n)
        elif len(descripciones) > 1:
            combinado = ''
            for d in descripciones:
                combinado += d.get_text(strip=True).encode('latin-1').decode('utf-8') + ' '
            descripcion.append(combinado.strip())

    #CONTENIDOS
        
df = pd.DataFrame({'Plataforma': coursera,
                   'URL del curso': link,
                   'Nombre del curso': nombre,
                   'Encargado del curso': encargado,
                   'Idioma del curso': idioma,
                   'Descripción del curso': descripcion,
                   'Metodología del curso': metodologia,
                   'Nivel del curso': nivel,
                   'Duración del curso': duracion,
                   'Precio del curso': precio,
                   'Certificación': certificacion
                   })

#df.to_csv('bm_coursera.csv', sep=';', encoding='utf-8-sig')
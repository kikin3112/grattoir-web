from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

pw_es = 'https://es.linkedin.com/learning/search?keywords=marketing+digital&upsellOrderOrigin=default_guest_learning&trk=learning-serp_learning-search-bar_search-submit&sortBy=RELEVANCE&entityType=COURSE'
pw_en = 'https://www.linkedin.com/learning/search?keywords=marketing+digital&upsellOrderOrigin=guest_homepage-basic_guest_nav_menu_learning&trk=learning-serp_learning-search-bar_search-submit&sortBy=RELEVANCE&entityType=COURSE'
r_resultado = requests.get(pw_en) #elegir idioma
sopa_resultado = bs(r_resultado.text, 'html.parser', from_encoding='utf-8')

box_results = sopa_resultado.find('ul', class_ = 'results-list')

linkedin = 'LINKEDIN'
modalidad = 'Curso'
idioma = 'Español'
metodologia = 'MOOC (xMOOC)'
certificacion = 'Disponible'
nombre = []
encargado = []
link = []
duracion = []
inscrito = [] #agregada

nombres = box_results.find_all('h3', class_ = 'base-search-card__title')
for i in nombres:
    n = i.get_text(strip=True)
    nombre.append(n) #clean_nombre

encargados = box_results.find_all('h4', class_ = 'base-search-card__subtitle')
for i in encargados:
    n = i.get_text(strip=True)
    encargado.append(n.replace('Por: ', '')) #clean_encargado

links = box_results.find_all('a', class_ = 'base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]')
for i in links:
    n = i.get('href')
    link.append(n) #clean_link

tiempos = box_results.find_all('div', class_ = 'search-entity-media__duration')
for i in tiempos:
    n = i.get_text(strip=True)
    duracion.append(n) #clean_duracion

inscritos = box_results.find_all('div', class_ = 'base-search-card__metadata')
for i in inscritos:
    metadata = i.find_all('span', class_='base-search-card__metadata-item')
    if len(metadata) > 1:
        views_text = metadata[0].get_text(strip=True)
        views = views_text.split()[0]
        inscrito.append(views) #clean_inscritos
    else:
        inscrito.append('No hay inscritos todavía.')

descripcion = []
contenido = []
nivel = []
precio = []

for l in link:
    r_curso = requests.get(l)
    sopa_curso = bs(r_curso.text, 'html.parser', from_encoding='utf-8')

    box_description = sopa_curso.find('section', class_ = 'core-section-container my-3 course-details')
    box_content = sopa_curso.find('section', class_ = 'table-of-contents mb-4 table-of-contents--with-max-height')
    box_level = sopa_curso.find('h2', class_ = 'top-card-layout__headline break-words font-sans text-md leading-open text-color-text')
    box_price = sopa_curso.find('form', class_ = 'buy-course-upsell__form')

    descripciones = box_description.find_all('div', class_ = 'show-more-less-html__markup')
    for d in descripciones:
        n = d.get_text(strip=True)
        descripcion.append(n) #clean_descripcion

    #CONTENIDO (Nombre módulo)
        
    titulo_modulo = box_content.find_all('button', class_ = 'show-more-less__button show-more-less__more-button show-more-less-button')
    cont_b_pp = []
    for c in titulo_modulo:
        n = c.get_text(strip=True)
        cont_b_pp.append(n)

    #CONTENIDO (Descripción módulo)
        
    descripcion_modulo = box_content.find_all('ul', class_ = 'show-more-less__list')
    cont_desc_pp = []
    for d in descripcion_modulo:
        items = d.find_all('div',  class_ = 'table-of-contents__item-title')
        textos = []
        for i in items:
            texto = i.get_text(strip=True)
            textos.append(texto)
        #OJO AL AHORRO DE LÍNEAS -> descriptions = [item.get_text(strip=True) for item in items]
        formato = ' - '.join(textos)
        cont_desc_pp.append(formato)

    #CONTENIDO (Nombre + descripción)

    pre_contenido = []
    for breve, full in zip(cont_b_pp, cont_desc_pp):
        combinado = ("{}: {}.\n\n".format(breve, full))
        pre_contenido.extend(combinado)
    final_contenido = ''.join(pre_contenido)
    contenido.append(final_contenido) #clean_contenido

    info = box_level.find_all('span', class_= 'top-card__headline-row-item')
    levels = info[3].get_text(strip=True).split(":")[1].strip()
    nivel.append(levels) #clean_nivel

    if box_price:
        precios = box_price.get_text(strip=True).split('(')[1].split(')')[0]
        final_precio = precios.replace('\xa0', ' ')
        precio.append(final_precio) #clean_precio
    else:
        precio.append('Precio no disponible.')

#pd.set_option('display.max_colwidth', None)

df = pd.DataFrame({'Plataforma': linkedin,
                   'Modalidad': modalidad,
                   'URL del curso': link,
                   'Nombre del curso': nombre,
                   'Encargado/s del curso': encargado,
                   'Idioma del curso': idioma,
                   'Descripción del curso': descripcion,
                   'Contenido del curso': contenido,
                   'Metodología del curso': metodologia,
                   'Nivel del curso': nivel,
                   'Duración del curso': duracion,
                   'Inscritos en el curso': inscrito,
                   'Precio del curso': precio,
                   'Certificación': certificacion
                   })

#df.head()
#df.to_csv('bm_linkedin.csv', sep=';', encoding='utf-8-sig')
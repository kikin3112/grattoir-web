import undetected_chromedriver as uc
import pyautogui
import time
import os
import win32clipboard

options = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=options)

ubi_default = r'C:\Users\luisr\Downloads'
destino_resultados = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Udemy\pw_resultados'
destino_cursos = r'C:\Users\luisr\OneDrive\Desktop\Consultoría\consultorio\scrape\Udemy\pw_cursos'

def comprobante(origen, nombre_archivo, destino):
        """
        Comprueba si el nombre_archivo.html ya se descargó y lo mueve del origen
        al destino.
        """
        existencia = os.path.join(origen, nombre_archivo + '.html')
        if os.path.exists(existencia):
            shutil.move(existencia, destino)
            return True
        return False

udemy = 'UDEMY'
modalidad = 'Course'
link = []
nombre = []
idioma = []
precio = []
descripcion = []
encargado = []

for i in range(2, 3):
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
    time.sleep(1)
    pyautogui.press('enter')

    win32clipboard.OpenClipboard()
    nombre_pw = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    while not comprobante(ubi_default, nombre_pw, destino_resultados):
        time.sleep(1)

    sopa_resultado = bs(open(destino_resultados + '\\' + nombre_pw + '.html', 'r'), 'html.parser')
    nombres = sopa_resultado.find_all('h3', class_='ud-heading-md course-card-title-module--course-title--wmFXN')
    for n in nombres:
        l = n.a.get('href')
        link.append(l) #clean_link
        textos = n.find_all('a')
        for t in textos:
            n = ''
            for i in t.contents:
                if not getattr(i, 'name', None) == 'div': #excluir div
                    n += str(i)
            #n = n.strip()
            nombre.append(n) #clean_nombre

nombres_html = []

for l in link:
    url = str(l)
    driver.get(url)

    pyautogui.press('esc')

    time.sleep(5)
    pyautogui.hotkey('ctrl','s')
    time.sleep(2)
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('ctrl','c')
    time.sleep(1)
    pyautogui.press('enter')

    win32clipboard.OpenClipboard()
    nombre_pw = win32clipboard.GetClipboardData()
    nombres_html.append(nombre_pw)
    win32clipboard.CloseClipboard()

    while not comprobante(ubi_default, nombre_pw, destino_cursos):
        time.sleep(1)
    
    time.sleep(1)

driver.quit()

for n in nombres_html:
    sopa_curso = bs(open(destino_cursos + '\\' + n + '.html', 'r'), 'html.parser')

    box_lang = sopa_curso.find('div', class_='clp-lead__element-item clp-lead__locale')
    box_price = sopa_curso.find('span', class_ = 'base-price-text-module--price-part---xQlz ud-clp-discount-price ud-heading-lg')
    box_description = sopa_curso.find('div', class_ = 'ud-text-sm component-margin styles--description--AfVWV')
    box_host = sopa_curso.find('span', class_ = 'instructor-links--names--fJWai')
    
    for l in box_lang:
        n = l.get_text(strip=True)
        idioma.append(n) #clean_idioma

    span = box_price.find_all('span')
    precios = span[1]
    for p in precios:
        n = p.get_text(strip=True)
        precio.append(n) #clean_precio

    descripciones = box_description.find_all('p')
    for d in descripciones:
        n = ' '.join(d.stripped_strings)
        descripcion.append(n) #clean_descripción

    instructor = encargados.find_all('a')
    nombres_instructor = []
    for i in instructor:
        n = i.get_text(strip=True)
        if '•' in n:
            n = n.split('•')[0].strip()
        nombres_instructor.append(n)    
    encargado.append(nombres_instructor) #clean_encargado

df = pd.DataFrame({'Plataforma': udemy,
                   'Modalidad': modalidad,
                   'URL del curso': link,
                   'Nombre del curso': nombre,
                   'Encargado/s del curso', encargado,
                   'Idioma del curso': idioma,
                   'Descripción del curso': descripcion,
                   'Precio del curso': precio
                   })
df.head()
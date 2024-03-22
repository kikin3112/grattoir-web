import undetected_chromedriver as uc
import pyautogui
import time
import os
import win32clipboard

options = uc.ChromeOptions()
driver = uc.Chrome(use_subprocess=True, options=options)

def comprobante(path, archivo):
        """
        Comprueba si el archivo.html ya se descargó.
        """
        existencia = os.path.join(path, archivo + '.html')
        return os.path.exists(existencia)

for i in range(1, 6):
    url = 'https://www.udemy.com/courses/search/?lang=en&lang=es&p=' + str(i) + '&q=marketing+digital&sort=relevance&src=ukw'
    print(url)
    driver.get(url)

    pyautogui.press('esc')

    time.sleep(5)
    pyautogui.hotkey('ctrl','s')
    time.sleep(1)
    pyautogui.press('right')
    pyautogui.press('_')
    pyautogui.press(str(i))
    time.sleep(1)
    pyautogui.hotkey('ctrl','a')
    pyautogui.hotkey('ctrl','c')
    time.sleep(1)
    pyautogui.press('enter')

    ubi = r'C:\Users\luisr\Downloads'
    win32clipboard.OpenClipboard()
    nombre = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    while not comprobante(ubi, nombre):
        time.sleep(1)
    time.sleep(1)

driver.quit()
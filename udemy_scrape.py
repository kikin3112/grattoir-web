import undetected_chromedriver as uc
from selenium import webdriver
import pyautogui
import time
import os
import win32clipboard

options = uc.ChromeOptions()

br = uc.Chrome(use_subprocess=True, options=options)  
br.get('https://www.udemy.com/courses/search/?lang=en&lang=es&q=marketing+digital&sort=relevance&src=ukw')
br.maximize_window()
pyautogui.press('esc')

time.sleep(5)
pyautogui.hotkey('ctrl','s')
time.sleep(1)
pyautogui.hotkey('ctrl','c')
time.sleep(1)
pyautogui.press('enter')

win32clipboard.OpenClipboard()
nombre = win32clipboard.GetClipboardData()
win32clipboard.CloseClipboard()

def check_for_file(filename, directory):
    """
    Check if a file with the given filename exists in the specified directory.
    """
    file_path = os.path.join(directory, filename + '.html')
    return os.path.exists(file_path)

# Specify the filename and directory to check

filename_to_check = nombre
download_directory = r'C:\Users\luisr\Downloads'  # Change this to your directory path

while not check_for_file(filename_to_check, download_directory):
    print(f"File '{filename_to_check}' does not exist in directory '{download_directory}'.")
    time.sleep(2)  # Wait for 2 seconds before checking again

print(f"File '{filename_to_check}' exists in directory '{download_directory}'. Stopping loop.")
br.quit()
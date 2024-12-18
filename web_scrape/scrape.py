import os
import re
import time
import pandas as pd

from utils.browser import WebDriver
from utils.eventos import registrar_evento
from PIL import Image, ImageEnhance, ImageOps

import pytesseract
# Definir o caminho do executável Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR"

URL_PENDENTES = "https://www.tjsp.jus.br/cac/scp/webRelPublicLstPagPrecatPendentes.aspx"
URL_EFETUADOS = "https://www.tjsp.jus.br/cac/scp/webrelpubliclstpagprecatefetuados.aspx"

def main(app_dir:str, cod_entidades:list, captchas:str):
    driver = WebDriver()
    baixar_pagamentos_pendentes(app_dir, driver, cod_entidades, captchas)
    driver.close_browser()


def baixar_pagamentos_pendentes(app_dir:str, driver:WebDriver, entidades:pd.DataFrame, captchas:pd.DataFrame):
    driver.open_url(URL_PENDENTES)
    driver.wait_selector('id', 'vENT_ID')

    for index, row in entidades.iterrows():
        url_captcha = driver.read_url('css', '[id="captchaImage"] > img' )
        num = re.findall('\d+', url_captcha)[0]
        baixado = False
        
        for i in range(0, 10):
            try:
                if i < 5: # Tenta ler os captchas pela lista
                    captcha = captchas.loc[int(num), 'captcha']
                else:
                    # Caso o captcha não esteja na lista o sistema tenta ler por OCR
                    captcha_dir = os.path.join(app_dir, 'temp', 'captcha.png')
                    captcha_path = driver.image_download('css', '[id="captchaImage"] > img', captcha_dir)
                    captcha = descaptchar(captcha_path) if captcha_path is not None else ''
                    while captcha == '':
                        driver.refresh()
                        captcha_path = driver.image_download('css', '[id="captchaImage"] > img', captcha_dir)
                        captcha = descaptchar(captcha_path) if captcha_path is not None else ''

                driver.write_text('id', '_cfield', captcha)
                time.sleep(2)          
                
                driver.select_by_value('id', 'vENT_ID', str(index))
                time.sleep(0.666)

                driver.btn_click('name', 'BUTTON3')
                com_erro = driver.element_exists('class', 'gx-warning-message', 0.666)

                if not com_erro:
                    baixado = True
                    break

                driver.refresh()
            except Exception as err:
                registrar_evento(err)

            if not baixado:
                registrar_evento(f"Erro ao tentar baixar {row['Entidade']}")


def baixar_pagamentos_efetuados(driver:WebDriver, entidades:pd.DataFrame, captchas:pd.DataFrame):
    driver.open_url(URL_EFETUADOS)
    driver.wait_selector('id', 'vENT_ID')

    for i, row in entidades:
        driver.select_by_value('id', 'vENT_ID', str(i))
        
        url_captcha = driver.read_url('css', '[id="captchaImage"] > img' )
        num = re.findall('\d+', url_captcha)[0]
        
        captcha = captchas.loc[int(num), 'captcha']
        driver.write_text('id', '_cfield', captcha)
        
        time.sleep(2)
        driver.btn_click('name', 'BUTTON3')


def descaptchar(image_path, val_enhace:int=2):    
    # Carregar a imagem
    image = Image.open(image_path)

    # 1. Converter para escala de cinza
    gray_image = ImageOps.grayscale(image)
    # gray_image.show()

    # 2. Aumentar o contraste
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(val_enhace)  # O valor 2 pode ser ajustado dependendo da imagem

    text = pytesseract.image_to_string(enhanced_image)
    text = re.sub("\W+","", text)

    if len(text) == 0 and val_enhace <= 5:
        return descaptchar(image_path, val_enhace+1)
    return text.lower()




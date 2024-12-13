import re
import os

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw

import pytesseract
# Definir o caminho do executável Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR"

def captcha_cross(image_path, val_enhace:int=2):    
    # Carregar a imagem
    image = Image.open(image_path)

    # 1. Converter para escala de cinza
    gray_image = ImageOps.grayscale(image)
    gray_image.show()

    # 2. Aumentar o contraste
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(val_enhace)  # O valor 2 pode ser ajustado dependendo da imagem

    text = pytesseract.image_to_string(enhanced_image)
    text = re.sub("\W+","", text)

    if len(text) == 0 and val_enhace <= 5:
        return captcha_cross(image_path, val_enhace+1)
    return text.lower()




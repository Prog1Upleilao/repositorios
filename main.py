import os
import re
from datetime import datetime

import pdfplumber
import scraping.scrape as scrape
import utils.ler_arquivos as leitura
from utils.eventos import registrar_evento


def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if not verificar_arquivos(app_dir):
        return False

    file_path = os.path.join(app_dir, 'processos.txt')    
    processos = leitura.ler_txt(file_path, True)
    
    ler_dados_pdf(app_dir, processos)
    return

    captcha_path = os.path.join(app_dir, 'files', 'lista_captcha.xlsx')
    entidades_path = os.path.join(app_dir, 'files', 'lista_entidades.xlsx')

    captchas = leitura.ler_xlsx(captcha_path, 'lista', 'num')
    cod_entidades = leitura.ler_xlsx(entidades_path, 'dados', 'Código', 'Leitura', 'sim')

    scrape.main(app_dir, cod_entidades, captchas)
    descompacta_arquivos(app_dir)


def descompacta_arquivos(app_dir:str)->list:
    # Pastas de origem e destino
    temp_path = os.path.join(app_dir, 'temp')
    downloads_path = os.path.expanduser("~/Downloads")
    os.makedirs(temp_path, exist_ok=True)

    # Lista para armazenar informações sobre os arquivos .zip
    pdf_files = []
    today_date = datetime.now().date()

    # Verifica todos os arquivos na pasta de downloads
    for file_name in os.listdir(downloads_path):
        if file_name.lower().endswith(".zip"):  # Filtra apenas arquivos .zip
            file_path = os.path.join(downloads_path, file_name)
            modification_time = os.path.getmtime(file_path)  # Tempo de modificação
            modification_datetime = datetime.fromtimestamp(modification_time)  # Converte para datetime

            # Verifica se o arquivo foi modificado hoje
            if modification_datetime.date() == today_date:
                leitura.descompactar_zip(file_path, temp_path)


def ler_dados_pdf(app_dir:str, processos:list):
    # Lê todos os arquivos da pasta 'temp'
    files_dir = os.path.join(app_dir, 'temp')
    if not os.path.exists(files_dir):
        registrar_evento("Pasta Temp não existe")
        return False
    
    pdfs_files = [file for file in os.listdir(files_dir) if file.lower().endswith('.pdf')]
    pdfs_files.reverse()

    for pdf in pdfs_files:
        pdf_path = os.path.join(files_dir, pdf)
        if not processos:
            break
        
        with pdfplumber.open(pdf_path) as pdf:
            precatorio = dict()
            
            for page in pdf.pages:
                texto_pagina = page.extract_text_lines()

                for linhas in texto_pagina:
                    texto = linhas['text']

                    if len(precatorio) == 7:
                        valores_nao_nulos = all(valor is not None for valor in precatorio.values())
                        if valores_nao_nulos:
                            processo = re.sub('\D+', '', precatorio['num_autos'])
                            if processo in processos:
                                processos.remove(processo)
                                precatorio.clear
                        
                    if re.match('^(ordem.*pagamento\:)', texto, flags=re.I):
                        ordem_pagamento = re.search('\d+', texto)
                        num_processo = re.search('\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', texto)
                        precatorio['ordem_pagamento'] = ordem_pagamento.group().strip() if ordem_pagamento else None
                        precatorio['num_processo'] = num_processo.group().strip() if num_processo else None
                    
                    if (re.match('^(natureza\:)', texto, re.I)):
                        natureza = re.search('\s.*', texto)
                        precatorio['natureza'] = natureza.group().strip() if natureza else None
                        
                    if (re.match('^(n.*de autos\:)', texto, re.I)):
                        num_autos = re.search('\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', texto)
                        ordem_orcamentaria = re.search('\d\/\d{4}', texto)
                        suspenso = re.search('(\s[a-z])$', texto, re.I)

                        precatorio['num_autos'] = num_autos.group().strip() if num_autos else None
                        precatorio['ordem_orcamentaria'] = ordem_orcamentaria.group() if ordem_orcamentaria else None
                        precatorio['suspenso'] = suspenso.group().strip() if suspenso else None
                    
                    if (re.match('^(data.*protocolo\:)', texto, re.I)):
                        data_protocolo = re.findall('\d{2}\/\d{2}\/\d{4}', texto)
                        if data_protocolo:
                            data_objeto = datetime.strptime(data_protocolo[0], r'%d/%m/%Y')
                            precatorio['data_protocolo'] = data_objeto


def verificar_arquivos(app_dir:str):
    nomes_pastas = ['arquivos', 'logs', 'temp']
    [os.makedirs(os.path.join(app_dir, n), exist_ok=True) for n in nomes_pastas]

    nomes_arquivos = ['lista_captcha.xlsx', 'lista_entidades.xlsx', 'processos.txt']
    com_arquivos = True
    for n in nomes_arquivos:
        file_path = os.path.join(app_dir, 'arquivos', n)
        if not os.path.exists(file_path):
            registrar_evento(f'"{n}" não existe')
            com_arquivos = False

    return com_arquivos


def add_dados_em_excel():
    pass


main()

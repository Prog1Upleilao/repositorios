import os
import re
import time
from datetime import datetime

import pdfplumber
from openpyxl import Workbook
from openpyxl.styles import Font
from  openpyxl import load_workbook
from openpyxl.styles import NamedStyle
from openpyxl.worksheet.dimensions import ColumnDimension
   
import web_scrape.scrape as scrape
import utils.ler_arquivos as leitura
from utils.eventos import registrar_evento


def main():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if not verificar_arquivos(app_dir):
        return False

    file_path = os.path.join(app_dir, 'arquivos', 'processos.txt')    
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

    for nome_pdf in pdfs_files:
        pdf_path = os.path.join(files_dir, nome_pdf)
        if not processos:
            break
        
        with pdfplumber.open(pdf_path) as pdf:
            precatorio = dict()
            precatorio['arquivo'] = nome_pdf

            for page in pdf.pages:
                texto_pagina = page.extract_text_lines()

                for linhas in texto_pagina:
                    texto = linhas['text']

                    if len(precatorio) == 8:
                        valores_nao_nulos = all(valor is not None for valor in precatorio.values())
                        processo = re.sub('\D+', '', str(precatorio.get('num_autos')))
                        if valores_nao_nulos and processo in processos:
                            escrever_dados(app_dir, precatorio)
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


def escrever_dados(app_dir:str, precatorio:dict):
    # criar o arquivo na primeira chamada
    file_path = os.path.join(app_dir, f'Relatório_{str(datetime.now().date())}.xlsx')
    if not os.path.exists(file_path):
        file_path = criar_arquivo_excel(app_dir)
    
    em_uso = True
    while em_uso:
        try:
            # Tentativa de abrir o arquivo em modo exclusivo
            with open(file_path, 'r+'):
                em_uso = False
        except IOError:
            print('Feche o Arquivo para eu poder salvar novos dados')

    # Carregar o arquivo existente
    workbook = load_workbook(file_path)
    # Verificar se a aba já existe
    if not 'Dados' in workbook.sheetnames:
        workbook.create_sheet(title='Dados')
    sheet = workbook['Dados']

    # Dados para adicionar
    data_formatada = precatorio.get('data_protocolo')
    new_data = [
        precatorio.get('num_autos'),
        precatorio.get('num_processo'),
        precatorio.get('natureza'),
        precatorio.get('ordem_orcamentaria'),
        precatorio.get('suspenso'),
        # precatorio.get('data_protocolo'),
        data_formatada.strftime("%d/%m/%Y") if data_formatada else '',
        precatorio.get('arquivo'),
        precatorio.get('ordem_pagamento'),
    ]
    
    # Identificar a próxima linha disponível
    next_row = sheet.max_row + 1

    # Adicionar os dados na próxima linha
    for col_index, value in enumerate(new_data, start=1):
        sheet.cell(row=next_row, column=col_index, value=value)

    # Salvar as alterações
    workbook.save(file_path)


def criar_arquivo_excel(app_dir:str, num_file:str=''):
    file_path = os.path.join(app_dir, f'Relatório_{str(datetime.now().date())}{num_file}.xlsx')
    
    # Criar o workbook e a planilha
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Dados'  # Nome da planilha

    # Definir os rótulos das colunas
    headers = ['Autos', 'Processo', 'Natureza', 'Ordem orçamentária', 'Suspenso?', 'Data do Protocolo', 'Arquivo', 'Ordem de Pagamento']

    # Adicionar os rótulos com formatação em negrito
    bold_font = Font(bold=True)
    for col_index, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col_index, value=header)
        cell.font = bold_font

    # Definir largura específica para as colunas
    column_widths = [24, 24, 17, 9, 9, 14, 37]  # Largura das colunas (ajuste conforme necessário)
    for col_index, width in enumerate(column_widths, start=1):
        column_letter = sheet.cell(row=1, column=col_index).column_letter
        sheet.column_dimensions[column_letter].width = width

    # Aplicar auto filtro aos rótulos
    sheet.auto_filter.ref = f"A1:H1"  # Ajuste o intervalo conforme o número de colunas

    # Congelar a primeira linha
    sheet.freeze_panes = "A2"  # Congela a linha acima da célula especificada (neste caso, a linha 1)

    # Salvar o arquivo Excel
    workbook.save(file_path)
    return file_path


main()
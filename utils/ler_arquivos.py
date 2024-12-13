""" Ler os dados de arquivos .xlsx, .xlsm, .csv, .txt"""
import re

import zipfile
import pdfplumber
import numpy as np
import pandas as pd

from utils.eventos import registrar_evento

    
def ler_xlsx(xlsx_path:str, sheet:str, index:str=None, rotulo_filtro:str=None, filtro:str=None)->pd.DataFrame:
    try:
        df = pd.read_excel(xlsx_path, sheet_name=sheet)
        if index:
            df.set_index(index, inplace=True)

        if rotulo_filtro and filtro:
            df = df[df[rotulo_filtro] == filtro]
        
        df.fillna('', inplace=True)
        return df
    
    except Exception as err:
        registrar_evento(err)
        return pd.DataFrame()
    
    
def lista_xlsx(xlsx_path:str, sheet:str, rotulo_retorno:str, rotulo_filtro:str=None, filtro:str=None)->np.array:
    try:
        df = ler_xlsx(xlsx_path, sheet)

        if rotulo_filtro and filtro:
            df = df[df[rotulo_filtro] == filtro]

        valores = np.array(df[rotulo_retorno].values)
        return valores
    
    except Exception as err:
        registrar_evento(err)
        return np.array()


def ler_pdf(path_file:str, is_table:bool=True, start_page:int=0, end_page:int=-1):
    try:
        with pdfplumber.open(path_file) as pdf:
            if end_page == -1:
                end_page = len(pdf.pages)
            elif end_page == start_page:
                end_page = start_page + 1
            
            paginas_intervalo = pdf.pages[start_page:end_page]
            data_page = []

            for _, page in enumerate(paginas_intervalo):  # Ajustar o número da página para exibição
                if is_table:
                    data_page.append(page.extract_tables())
                else:
                    data_page.append(page.extract_text_lines())

            if is_table:
                data_list = [cell for page in data_page if page for row in page if row for cell in row]
            else:
                data_list = [line['text'] for page in data_page if page for line in page]
            
            return data_list

    except Exception as err:
        registrar_evento(f'Erro ao tentar ler o arquivo {path_file}')
        return []


def ler_txt(file_path:str, is_list:bool):
    try: 
        with open(file_path, "r", encoding="utf-8") as arquivo:
            if is_list:
                linhas = arquivo.readlines()
                # 0031721-39.2022.8.26.0053
                processos = [re.sub('[\W\_]+', '', l) for l in linhas]
                processos = [l for l in processos if len(l) == 20]
                return processos
            else:
                texto = arquivo.read()
                return texto
        
    except Exception as err:
        return []


def descompactar_zip(zip_path:str, destino_path:str):
    try:
        # Abrindo o arquivo .zip e extraindo os arquivos
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destino_path)

    except Exception as err:
        registrar_evento(err)
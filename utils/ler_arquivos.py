""" Ler os dados de arquivos .xlsx, .xlsm, .csv, .txt"""
import re

import zipfile
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


def ler_txt(file_path:str, is_list:bool):
    try: 
        with open(file_path, "r", encoding="utf-8") as arquivo:
            if is_list:
                linhas = arquivo.readlines()
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
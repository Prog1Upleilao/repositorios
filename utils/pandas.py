import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
import pandas as pd
import numpy as np

from utils.eventos import registrar_evento

user = os.getenv('USER_DB')
password =  quote_plus(os.getenv('PASS_DB'))
host = os.getenv('HOST_DB')

def consultar_dados(query, database=os.getenv('DB_JURISPRUDENCIAS'), index=None):
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
        df = pd.read_sql_query(query, engine)
        if index != None:
            df.set_index(index, inplace=True)
        return df
    
    except Exception as err:
        registrar_evento(err)
        return []
    

def consultar_dados_numpy(query, rotulo, database=os.getenv('DB_JURISPRUDENCIAS')):
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
        df = pd.read_sql_query(query, engine)
        valores = np.array(df[rotulo].values)
        return valores

    except Exception as err:
        registrar_evento(err)
        return None
import os

import mysql.connector as connector
from mysql.connector import Error
from mysql.connector.connection_cext import CMySQLConnection
from utils.eventos import registrar_evento

config = {
    "host" : os.getenv("HOST_DB"),
    "database": os.getenv("DB_JURISPRUDENCIAS"),
    "user" : os.getenv("USER_DB"),
    "password" :  os.getenv("PASS_DB")
}


def conectar_db(nome_banco=None)->CMySQLConnection:
    """ Conecta ao banco de dados jurisprudencias """
    if nome_banco:
        config["database"] = nome_banco

    try:
        con = connector.connect(**config)
        return con
    
    except Error as err:
        registrar_evento(f"Erro ao tentar se conectar ao DB {nome_banco} -> {err}")

    return None


def salvar_db(query:str, registros, con:CMySQLConnection, cursor1=None):
    """ Registros devem ser tuplas """
    
    cursor = con.cursor() if not cursor1 else cursor1
    try:
        con.start_transaction()
        cursor.executemany(query, registros)
        con.commit()

    except Error as err:
        #  Reverte a transação se houver erro
        con.rollback()

        if len(registros) < 2:
            registrar_evento(f"Não registrado -> {registros}")
            return None
        
        meio = len(registros) // 2
        registros1 = registros[meio:]
        registros2 = registros[:meio]

        # Recursão para tentar inserir as duas metades
        salvar_db(con, cursor, query, registros1)
        salvar_db(con, cursor, query, registros2)
    
    # Fecha o cursor caso ele não seja passado por parâmetro
    if not cursor1:
        cursor.close()


def consultar_data_atualizacao(con:CMySQLConnection):
    """ Retornar a data de atualização da tabela "_atualizacao" """
    try:
        cursor = con.cursor()
        query = f"SELECT data_recente FROM _atualizacao WHERE id = '{id}' LIMIT 1"
        
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result[0]
    
    except Exception as err:
        registrar_evento(err)
        return None


def consultar_dados(query, con:CMySQLConnection):
    """ Retorna valores dos banco de dados, utilizando o mysql-connector """
    try:
        cursor = con.cursor()
        cursor.execute(query)

        result = cursor.fetchall()
        cursor.close()
        return result
    
    except BaseException as err:
        registrar_evento(err)
        return None


if __name__ == "__main__":
    """ Chamada direta somente para testes """

    # con = conectar_db()
    # data = consultar_data(con, "stj0")
    # print(data)

    # con.close()
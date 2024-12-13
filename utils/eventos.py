import os
import inspect
from datetime import datetime


def registrar_evento(detalhe=""):
    """
    Função para registrar eventos em um arquivo de log diário.
    """

    # obtém a pasta pai do arquivo atual
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)

    # Obtém a data atual no formato aaaa-mm-dd
    data_atual = str(datetime.now())[:10]
    nome_log = f"{data_atual}.log"
    log_path = os.path.join(parent_dir, "logs", nome_log)
    
    # Verifica se o arquivo já existe, se não, cria um novo com cabeçalho
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("Date - Time      | File Name                     | Function Name                 | Evento\n")
            log_file.write("-" * 120 + "\n")
    
    # Obtém o frame da função que chamou esta função
    caller_frame = inspect.stack()[1]
    
    linha_log = formatar_linha(caller_frame, detalhe)
    
    # Registra o erro no arquivo do dia
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(linha_log)


def formatar_linha(caller_frame, detalhe=""):
    # Pega o caminho completo do arquivos
    full_path = caller_frame.filename

    # Extrai o caminho relativo a partir da pasta "PROJETO"
    nome_arquivo = os.path.basename(full_path)
    nome_funcao = caller_frame.function
    nome_arquivo = nome_arquivo + (" " * abs(30 - len(nome_arquivo)))
    nome_funcao = nome_funcao + (" " * abs(30 - len(nome_funcao)))
    
    linha_log = f"{str(datetime.now())[:16]} | {nome_arquivo}| {nome_funcao}| {detalhe}\n"
    return linha_log


if __name__ == "__main__":
    # Exemplo de uso
    registrar_evento("Erro de exemplo")
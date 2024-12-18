import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image # pillow

from utils.eventos import registrar_evento

class WebDriver:

    def __init__(self, browser_oculto:bool=False):
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        chrome_options.add_argument("--start-maximized") # maxim
        chrome_options.add_argument("--enable-blink-features=IdleDetection")
        chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        chrome_options.add_argument("--ignore-certificate-errors") # ignora erros de certificado
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        if browser_oculto:
            chrome_options.add_argument("--headless")  # Ativa o modo headless
        
        # Desabilitar automação para evitar ser detectado como bot
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        
        """ Caso ocorra erro de conexão, verifique o site abaixo está disponível 
        https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json
        """
        # Inicializar o driver com as opções configuradas
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.maximize_window()

        # Define o mapeamento de tipos de seletores para Selenium
        self.seletores = {
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
            "id": By.ID,
            "link": By.LINK_TEXT,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "xpath": By.XPATH
        }
        
    def open_url(self, url:str):
        """Abre a URL especificada no navegador na aba atual."""
        try:
            self.driver.get(url)
            return True
        
        except Exception as err:
            print(f"Erro ao tentar acessar {url} -> {err}")
            return False

    def refresh(self):
        self.driver.refresh()

    def close_browser(self, wait_for_close:float=1.666):
        """Fecha o navegador completamente."""
        time.sleep(wait_for_close)
        try:
            self.driver.quit()
        except Exception as err:
            print(f"Erro ao tentar fechar o navegador -> {err}")
        
    def new_tab(self, url:str=""):
        """Abre uma nova aba e navega para a URL especificada."""
        try:
            self.driver.execute_script(f"window.open('{url}', '_blank');")
        except Exception as err:
            print(f"Erro ao tentar criar uma nova aba -> {err}")

    def alternate_tab(self, tab_index:int):
        """ Alterna para a aba especificada pelo índice."""
        abas = self.driver.window_handles
        try:
            if tab_index < len(abas):
                self.driver.switch_to.window(abas[tab_index])
            else:
                print(f"Erro: Não há aba disponível para o índice {tab_index}")
                
        except Exception as err:
            print(f"Erro ao tentar altarnar entre abas -{err}")

    def title_tab(self):
        """Retorna o título da aba atual."""
        try:
            titulo = self.driver.title
            return titulo
        except:
            return None

    def close_tab(self, tab_index:int=-1):
        """Fecha a aba especificada pelo índice, se não especificar a atual será fechada """
        abas = self.driver.window_handles
        if tab_index < len(abas) and tab_index >= 0:
            # Alterna para a aba pelo índice e fecha
            self.driver.switch_to.window(abas[tab_index])
        
        if len(abas) > 1:
            self.driver.close()
        else:
            self.driver.quit()
        
        # Após fechar, o controle precisa ser mudado para outra aba
        if tab_index > 0:
            self.driver.switch_to.window(abas[tab_index-1])  # Alterna para a última aba aberta

    def wait_selector(self, seletor_tipo:str, seletor:str, espera:float=30):
        """ Espera um elemento estar disponível, não precisa registrar erro em log """
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            return True

        except Exception as err:
            registrar_evento(f"Sistema não encontrou o elemento {seletor}")
            return False
    
    def element_exists(self, seletor_tipo:str, seletor:str, espera:float=30):
        """ Verifica a existência de um elemento """
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            return True

        except Exception as err:
            return False

    def btn_click(self, seletor_tipo:str, seletor:str, espera:float=30):
        """ Verifica se o elemento existe clica nele """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            element = WebDriverWait(self.driver, espera).until(EC.visibility_of_element_located((self.seletores[seletor_tipo], seletor)))

            # Simula o hover usando ActionChains antes de clicar
            hover_action = ActionChains(self.driver)
            hover_action.move_to_element(element).perform()

            element.click()
            return True
        
        except Exception as err:
            registrar_evento(f"Erro ao tentar clicar em {seletor}")
            return False
    
    def check_box(self, seletor_tipo:str, seletor:str, marcar:bool=True, espera:float=30):
        """ Verifica se o check box está visível clica nele """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            checkbox = WebDriverWait(self.driver, espera).until(EC.visibility_of_element_located((self.seletores[seletor_tipo], seletor)))

            # Simula o hover usando ActionChains antes de clicar
            hover_action = ActionChains(self.driver)
            hover_action.move_to_element(checkbox).perform()

            if not checkbox.is_selected() and marcar or checkbox.is_selected() and not marcar:
                checkbox.click()
            return True
        
        except Exception as err:
            registrar_evento(f"Erro ao tentar clicar em {seletor}")
            return False

    def read_text(self, seletor_tipo:str, seletor:str, espera:float=30):
        """ Lê o texto de um seletor específico """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            return element.text
        
        except Exception as err:
            registrar_evento(f"Erro ao tentar ler o texto de {seletor}")
            return None

    def read_url(self, seletor_tipo:str, seletor:str, espera:float=30):
        """ Lê o texto de um seletor específico """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            url = element.get_attribute('src')
            return url
        
        except Exception as err:
            registrar_evento(f"Erro ao tentar ler o texto de {seletor}")
            return None

    def write_text(self, seletor_tipo:str, seletor:str, texto:str, espera:float=30):
        """ Escrever valores em um seletor específico """

        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))           
            
            # Simula o hover usando ActionChains antes de clicar
            hover_action = ActionChains(self.driver)
            hover_action.move_to_element(element).perform()
            
            # Limpa o campo antes da escrita
            element.clear()

            element.send_keys(texto)
            return True
        
        except Exception as err:
            registrar_evento(f"Erro ao tentar escrever {texto} em {seletor}")
            return False
    
    def return_selector_list(self, seletor_tipo:str, seletor:str, espera: float=30):
        """ Retorna lista de elementos específicos """

        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            # Espera até que o elemento esteja presente e retorna o elemento localizado
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_all_elements_located((self.seletores[seletor_tipo], seletor)))
            return element

        # Tratar exceções específicas para depuração mais fácil
        except Exception as err:
            registrar_evento(f"Erro ao localizar o elemento: {seletor}")
            return [] # retornar vazio para não precisar verificar valor antes de iterar sobre a lista
        
    def return_selector_unique(self, seletor_tipo:str, seletor:str, espera: float=30):
        """ Retorna um elementos específico da página """

        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            # Espera até que o elemento esteja presente e retorna o elemento localizado
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            return element
        
        # Tratar exceções específicas para depuração mais fácil
        except Exception as err:
            print(f"Erro ao localizar o elemento: {seletor}")
            return None
    
    def return_values_list(self, seletor_tipo:str, seletor:str, espera: float=30):
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        
        try:
            # Espera até que o elemento esteja presente e retorna o elemento localizado
            element = WebDriverWait(self.driver, espera).until(
                EC.presence_of_all_elements_located((self.seletores[seletor_tipo], seletor))
                )
            # Retorna a lista em string
            valores = [e.text for e in element]
            return valores
        
        except Exception as err:
            registrar_evento(f"Erro ao localizar o elemento: {seletor}")
            return []
        
    def return_value_unique(self, seletor_tipo:str, seletor:str, espera: float=30):
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        
        try:
            # Espera até que o elemento esteja presente e retorna o elemento localizado
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            # Retorna apenas o texto do seletor
            return element.text
        
        except Exception as err:
            registrar_evento(f"Erro ao localizar o elemento: {seletor}")
            return None
    
    def page_to_frame(self, seletor_tipo:str, seletor:str, espera:float=60):
        """ Aponta para a página"""
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        
        try:
            WebDriverWait(self.driver, espera).until(EC.frame_to_be_available_and_switch_to_it((seletor_tipo, seletor)))
        except:
            registrar_evento(f"Erro ao tentar entrar no Frame: seletor")
            return False
    
    def frame_to_page(self):
        """ Sai do frame e retorna aponta para a página"""
        try:
            self.driver.switch_to.default_content()
        except:
            return False
    
    def execute_script(self, chamada_funcao:float):
        try:
            self.driver.execute_script(chamada_funcao)
            return True
        except Exception as err:
            registrar_evento(f"Erro ao tentar executar a função {chamada_funcao}")
            return False            

    def hover(self, seletor_tipo, seletor, espera:float=30):
        """ Simula a posição do mouse sobre o seletor """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()  # Simula hover

        except Exception as err:
            pass

    def select_by_value(self, seletor_tipo, seletor, selecao=any, espera:float=30):
        """ Seleciona vários elementos caso 'selecao' seja uma lista e apenas um elemento caso seja string """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            select = Select(element)

            if isinstance(selecao, list):
                [select.select_by_value(s) for s in selecao]
            else:
                select.select_by_value(selecao)

            return True
        except Exception as err:
            registrar_evento(f"Erro ao tentar selecionar elementos em {seletor}")
            return False
    
    def list_select_options(self, seletor_tipo, seletor, espera: float = 30):
        """
        Lista os valores (value) e textos (text) de todas as opções de um elemento <select>.
        
        Args:
            driver: Instância do WebDriver do Selenium.
            seletor_tipo: Tipo de seletor (e.g., "id", "xpath", "css selector").
            seletor: O seletor para localizar o elemento <select>.
            espera: Tempo máximo para esperar o elemento estar presente.
        
        Returns:
            Uma lista de dicionários contendo 'value' e 'text' de cada opção.
        """
        
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        
        try:
            # Espera o elemento <select> estar presente
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            select = Select(element)

            # Lista as opções do <select>
            opcoes = [{"value": option.get_attribute("value"), "text": option.text} for option in select.options]
            return opcoes
        
        except Exception as err:
            print(f"Erro ao listar opções do select: {err}")
            return []

    def select_by_index(self, seletor_tipo, seletor, selecao=list, espera:float=30):
        """ Seleciona valores de uma caixa de seleção passando os indexies """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            select = Select(element)
            [select.select_by_index(s) for s in selecao]

        except Exception as err:
            registrar_evento(f"Erro ao tentar selecionar indexies em {seletor}")

    def image_download(self, seletor_tipo:str, seletor:str, img_path:str, espera:float=30):
        """ Realiza o download de uma imagem específica """
        if seletor_tipo not in self.seletores:
            raise ValueError(f"Tipo de seletor '{seletor_tipo}' inválido. Use um dos seguintes: {', '.join(self.seletores.keys())}")
        try:
            element = WebDriverWait(self.driver, espera).until(EC.presence_of_element_located((self.seletores[seletor_tipo], seletor)))
            
            # Localiza posição e tamanho da imagem
            location = element.location
            size = element.size

            # Salva a captura de página inteira
            self.driver.save_screenshot(img_path)
            page_image = Image.open(img_path)

            captcha = page_image.crop((
                location["x"], # Pega eixo x da imagem 
                location["y"], # Pega eixo y da imagem 
                location["x"] + size["width"], # Pega largura da imagem 
                location["y"] + size["height"], # Pega altura da imagem
            ))

            captcha.save(img_path)
            if os.path.exists(img_path):
                return img_path
            return None
        
        except Exception as err:
            registrar_evento(err)
            return None

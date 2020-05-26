#!/usr/bin/env python
""" Módulo para mala direta em whatsapp .
Código baseado em https://github.com/rxrichard/sending-message-whatsapp-simple de rxrichard Richard Bastos
.
Copyright (c) 2020 Eduardo Lima Marcelino

 É concedida permissão, gratuitamente, a qualquer pessoa que obtenha uma cópia
 deste software e arquivos de documentação associados (ao "Software"), para usa-lo
 sem restrição, incluindo, sem limitação, os direitos de 
 usar, copiar, modificar, mesclar, publicar, distribuir, sublicenciar e / ou vender
 cópias do Software e permitir pessoas a quem o Software está
 instalado para fazê-lo, sujeito às seguintes condições:

 O aviso de direitos autorais acima e este aviso de permissão serão incluídos em
 todas as cópias ou partes substanciais do Software.

 O SOFTWARE É FORNECIDO "TAL COMO ESTÁ", SEM GARANTIA DE QUALQUER TIPO, EXPLICITA OU
 IMPLÍCITA, INCLUINDO MAS NÃO SE LIMITANDO A GARANTIAS DE COMERCIALIZAÇÃO,
 APTIDÃO PARA UM OBJETIVO ESPECÍFICO E NÃO INFRAÇÃO. EM NENHUM CASO OS
 AUTORES OU TITULARES DE DIREITOS AUTORAIS SÃO RESPONSÁVEIS POR QUALQUER REIVINDICAÇÃO, DANOS OU OUTRA
 RESPONSABILIDADE, SEJA EM AÇÃO DE CONTRATO, OU DE OUTRA FORMA DECORRENTE DE USO,
 FORA OU EM CONEXÃO COM O SOFTWARE OU O USO EM OUTRAS APLICAÇÕES DE SOFTWARE.
"""

__author__ = "Eduardo Lima Marcelino"
__authors__ = ["Eduardo Lima Marcelino dumarcelino@gmail.com", "Richard Bastos @rxrichard"]
__contact__ = "dumarcelino@gmail.com"
__copyright__ = "Copyright 2020, Clicosim"
__credits__ = ["Richard Bastos @rxrichard", "dumarcelino@gmail.com"]
__date__ = "2020-04-10"
__deprecated__ = False
__email__ =  "dumarcelino@gmail"
__license__ = "MIT"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

#######################
# lista de dependencias
#######################
from time import sleep
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import socket
import csv      # import para leitura csv
import logging  # import para criação de log
import datetime # importa datetime e time para nome log
import os       # import para renomear arquivos

####################
# Parâmetros gerais
####################

# tempos
validawz = 30    # aguardar validação QRcode Whatsapp
esperaenvio = 45 # aguardar até digitar mensagem valor sugerido = 30
esperaerros = 120 # aguardar tempo até enviar novamente após 2 erros seguidos
esperavezes = 0  # aguardar para enviar novamente mensagem para o mesmo telefone

inicio = datetime.datetime.now()

# outros parâmetros
csv_arquivo = 'contatos.csv'            # nome da lista a ser usada para envio
csv_entrada = 'contatos_'+inicio.strftime('%Y-%m-%d-%H-%M-%S')+'.csv'     # contatos em uso
csv_ok = 'contatos_ok_'+inicio.strftime('%Y-%m-%d-%H-%M-%S')+'.csv'       # envios ok
csv_erros = 'contatos_erros_'+inicio.strftime('%Y-%m-%d-%H-%M-%S')+'.csv' # falhas no envio
csv_separacampo = ';'                   # separador de campos do arquivo csv
csv_limitadortxt = '"'                  # delimitador de texto dentro dos campos para mensagem com quebra de linha
no_of_message = 1                       # QUANTIDADE DE VEZES A SER ENVIADA PARA A MESMA PESSOA
urlwhatsweb = "http://web.whatsapp.com" # url de acesso ao whatsapp web

########################
# Layout do csv exemplo
# fone;msg;DATA_CONTATO
# 5511999999999;"mensagem a ser enviada";23/04/2020




# configurando saída do log ( DEBUG INFO WARNING ERROR CRITICAL )
logging.basicConfig(filename='envio-'+inicio.strftime('%Y-%m-%d-%H-%M-%S')+'.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

logging.warning('Iniciando envio em: '+inicio.strftime('%Y-%m-%d-%H-%M-%S'))

# Estatísticas
total = 0        # envios acumulados
sucesso = 0      # número acumulado de sucessos
falha = 0        # número acumulado de falhas
falhaseguida = 0 # falhas consecutivas



# arquivos a serem criados/abertos
os.rename(csv_arquivo,csv_entrada)
arquivo = open(csv_entrada)       # arquivo de dados de envio
envioOk = open(csv_ok, 'w')       # arquivo de números que receberam a mensagem
envioFalha = open(csv_erros, 'w') # arquivo de numeros que não receberam a mensagem


# carregando linhas
moblie_no_list = csv.DictReader(arquivo, delimiter=csv_separacampo, quotechar=csv_limitadortxt)
escreveOk = csv.DictWriter(envioOk,delimiter=csv_separacampo, quotechar=csv_limitadortxt, quoting=csv.QUOTE_ALL,fieldnames=moblie_no_list.fieldnames)
escreveErro = csv.DictWriter(envioFalha, delimiter=csv_separacampo, quotechar=csv_limitadortxt, quoting=csv.QUOTE_ALL,fieldnames=moblie_no_list.fieldnames)


escreveOk.writeheader()
escreveErro.writeheader()

def element_presence(by, xpath, time):
    element_present = EC.presence_of_element_located((By.XPATH, xpath))
    WebDriverWait(driver, time).until(element_present)


def is_connected():
    try:
        # verifica conexão com internet
        socket.create_connection(("www.google.com", 80))
        return True
    except:
        is_connected()


driver = webdriver.Chrome(executable_path="chromedriver.exe")

driver.get(urlwhatsweb)
sleep(validawz)  # aguarda o scan do codigo do wz

# noinspection PyDeprecation
def send_whatsapp_msg(phone_no, text):
    driver.get("https://web.whatsapp.com/send?phone={}&source=&data=#".format(phone_no))
    global total
    total += 1
    # iniciar tentativa de envio
    try:
        driver.switch_to_alert().accept()
    except Exception as e:
        pass

    try:
        element_presence(By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]', esperaenvio)
        txt_box = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        global falhaseguida
        if falhaseguida > 1:
            sleep (esperaerros)
            falhaseguida = 0
        global no_of_message
        for x in range(no_of_message):
            txt_box.send_keys(text)
            txt_box.send_keys("\n")
            global esperavezes
            sleep (esperavezes)
        global sucesso
        sucesso += 1
        # gravar envio ok
        escreveOk.writerow({'fone': phone_no, 'msg': text})
    except Exception as e:
        print("invalid phone no :" + str(phone_no))
        logging.error('Telefone inválido: '+ str(phone_no))
        global falha
        falha += 1
        #global falhaseguida
        falhaseguida += 1
        # gravar falha envio
        escreveErro.writerow({'fone': phone_no, 'msg': text})
        sleep(esperaerros)
for moblie_no in moblie_no_list:
    try:
        logging.warning('Enviando mensagem para o número: ' + moblie_no["fone"])
        send_whatsapp_msg(moblie_no["fone"], moblie_no["msg"])
        
        
    except Exception as e:
        logging.error('Falha desconhecida no envio: '+ moblie_no["fone"])
        # gravar falha envio
        escreveErro.writerow({'fone': moblie_no["fone"], 'msg': moblie_no["msg"]})

        sleep(esperaerros)
        is_connected()

driver.quit() #finalizar chrome após fim do envio
fim = datetime.datetime.now()
tempototal = fim - inicio
logging.warning('Finalizando envio... EEEEEEE :-D - '+fim.strftime('%Y-%m-%d-%H-%M-%S')+' tempo total de execução: '+str(tempototal)+' Total Contatos: '+ str(total)+' OK: '+ str(sucesso)+' Falhas: '+ str(falha)+' Aproveitamento: '+ str(round((sucesso / total * 100),2))+'%')

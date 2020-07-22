import pyodbc
import os
import XmlGenerator as xml_creator
import subprocess
import datetime
import time
import base64
from rauth import OAuth2Service
import json
import requests
import getpass
import xmltodict


conn = pyodbc.connect(
    r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\PUNTOVENTA\\ANDROMEDA.accdb;')
cursor = conn.cursor()
base_path = "/PUNTOVENTA/Hermes/Documentos"


def oauth_decode(data):
    new_data = data.decode("utf-8", "strict")
    return json.loads(new_data)


def get_current_datetime():
    timezone = datetime.timezone(datetime.timedelta(hours=-6))
    current_datetime = datetime.datetime.now(timezone)
    return current_datetime.strftime('%Y-%m-%dT%H:%M:%S-06:00')


def send_data(user_data, xml_data, sender_id_type, sender_id_number, receiver_id_type=None,
              receiver_id_number=None, doc_key=0, ticket=True):

    
    
    service = OAuth2Service(name="production",
                            client_id="api-prod",
                            client_secret="",
                            access_token_url="https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token")


    data = {'grant_type': 'password',
            'username': '{}@prod.comprobanteselectronicos.go.cr'.format(user_data.get("access")),
            'password': '{}'.format(user_data.get("password"))}

    url_send = "https://api.comprobanteselectronicos.go.cr/recepcion/v1/recepcion"

    """

    service = OAuth2Service(
        name="sandbox",
        client_id="api-stag",
        client_secret="",
        access_token_url="https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token"
    )

    data = {'grant_type': 'password',
            'username': '{}@stag.comprobanteselectronicos.go.cr'.format(user_data.get("access")),
            'password': '{}'.format(user_data.get("password"))}

    url_send = "https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/recepcion"

    """    
   

    session = service.get_auth_session(data=data, decoder=oauth_decode)

    access_token = session.access_token

    headers = {"Authorization": "Bearer " + access_token}

    print(f"Enviando: {doc_key}")

    if ticket:
        json_data = """{"clave": "%s", "fecha": "%s", "emisor": {"tipoIdentificacion": "%s",
                "numeroIdentificacion": "%s"},"comprobanteXml": "%s"}""" % (doc_key, get_current_datetime(),
                                                                            sender_id_type, sender_id_number,
                                                                            xml_data)

    else:
        json_data = """{"clave": "%s", "fecha": "%s", "emisor": {"tipoIdentificacion": "%s",
        "numeroIdentificacion": "%s"}, "receptor": {"tipoIdentificacion": "%s","numeroIdentificacion": "%s"},
        "comprobanteXml": "%s"}""" % (doc_key, get_current_datetime(),
                                      sender_id_type, sender_id_number,
                                      receiver_id_type, receiver_id_number, xml_data)

    if True:
        response = requests.post(url_send, json_data, headers=headers)
        print(response)
        print("Respuesta: ", response.text)
        if "error" in response.text:
            return False

        else:
            print(response)
            return True

    else:
        return False


def send_credit_xml(ticket, user_data):
    directory_path = "{}/{}/NC/{}/".format(
        base_path, user_data.get("id_number"), ticket[1].strftime('%Y-%m-%d'))
    file_name = "{}.xml".format(ticket[0])
    if os.path.isfile('{}{}'.format(directory_path, file_name)):

        file_pointer = open("{}{}".format(
            directory_path, file_name.strip()), 'r', encoding='utf-8')
        file_data = file_pointer.read()

        dictionary_data = xmltodict.parse(file_data, encoding="utf-8")
        dictionary_data = dictionary_data["NotaCreditoElectronica"]
        sender_id_type = dictionary_data["Emisor"]["Identificacion"]["Tipo"]
        sender_id_number = dictionary_data["Emisor"]["Identificacion"]["Numero"]
        doc_key = dictionary_data["Clave"]

        xml_to_send = base64.b64encode(
            file_data.encode('utf-8')).decode('utf-8')
        return send_data(user_data=user_data, xml_data=xml_to_send,
                         sender_id_type=sender_id_type, sender_id_number=sender_id_number,
                         doc_key=doc_key, ticket=True)
    else:
        print("{} no existe.".format(file_name))
        return False


def send_debit_xml(ticket, user_data):
    directory_path = "{}/{}/ND/{}/".format(
        base_path, user_data.get("id_number"), ticket[1].strftime('%Y-%m-%d'))
    file_name = "{}.xml".format(ticket[0])
    if os.path.isfile('{}{}'.format(directory_path, file_name)):

        file_pointer = open("{}{}".format(
            directory_path, file_name.strip()), 'r', encoding='utf-8')
        file_data = file_pointer.read()

        dictionary_data = xmltodict.parse(file_data, encoding="utf-8")
        dictionary_data = dictionary_data["NotaDebitoElectronica"]
        sender_id_type = dictionary_data["Emisor"]["Identificacion"]["Tipo"]
        sender_id_number = dictionary_data["Emisor"]["Identificacion"]["Numero"]
        doc_key = dictionary_data["Clave"]

        xml_to_send = base64.b64encode(
            file_data.encode('utf-8')).decode('utf-8')
        return send_data(user_data=user_data, xml_data=xml_to_send,
                         sender_id_type=sender_id_type, sender_id_number=sender_id_number,
                         doc_key=doc_key, ticket=True)
    else:
        print("{} no existe.".format(file_name))
        return False


def send_ticket_xml(ticket, user_data):
    directory_path = "{}/{}/Tiquetes/{}/".format(
        base_path, user_data.get("id_number"), ticket[1].strftime('%Y-%m-%d'))
    file_name = "{}.xml".format(ticket[0])
    if os.path.isfile('{}{}'.format(directory_path, file_name)):
        print("Abriendo: {}".format(file_name.strip()))
        file_pointer = open("{}{}".format(
            directory_path, file_name.strip()), 'r', encoding='utf-8')
        file_data = file_pointer.read()

        dictionary_data = xmltodict.parse(file_data, encoding="utf-8")
        dictionary_data = dictionary_data["TiqueteElectronico"]
        sender_id_type = dictionary_data["Emisor"]["Identificacion"]["Tipo"]
        sender_id_number = dictionary_data["Emisor"]["Identificacion"]["Numero"]
        doc_key = dictionary_data["Clave"]

        xml_to_send = base64.b64encode(
            file_data.encode('utf-8')).decode('utf-8')
        return send_data(user_data=user_data, xml_data=xml_to_send,
                         sender_id_type=sender_id_type, sender_id_number=sender_id_number,
                         doc_key=doc_key, ticket=True)
    else:
        print("{} no existe.".format(file_name))
        return False


def send_bill_xml(bill, user_data):
    directory_path = "{}/{}/Facturas/{}/".format(
        base_path, user_data.get("id_number"), bill[1].strftime('%Y-%m-%d'))
    file_name = "{}.xml".format(bill[0])
    # print(directory_path, file_name)
    if os.path.isfile('{}{}'.format(directory_path, file_name)):
        file_pointer = open("{}{}".format(
            directory_path, file_name.strip()), 'r', encoding='utf-8')
        file_data = file_pointer.read()

        dictionary_data = xmltodict.parse(file_data, encoding="utf-8")
        dictionary_data = dictionary_data["FacturaElectronica"]
        sender_id_type = dictionary_data["Emisor"]["Identificacion"]["Tipo"]
        sender_id_number = dictionary_data["Emisor"]["Identificacion"]["Numero"]
        receiver_id_type = dictionary_data["Receptor"]["Identificacion"]["Tipo"]
        receiver_id_number = dictionary_data["Receptor"]["Identificacion"]["Numero"]
        doc_key = dictionary_data["Clave"]

        xml_to_send = base64.b64encode(
            file_data.encode('utf-8')).decode('utf-8')
        return send_data(user_data=user_data, xml_data=xml_to_send,
                         sender_id_type=sender_id_type, sender_id_number=sender_id_number,
                         receiver_id_type=receiver_id_type, receiver_id_number=receiver_id_number,
                         doc_key=doc_key, ticket=False)
    else:
        print("{} no existe.".format(file_name))
        return False


def get_to_send_data(user_data):

    user_code = user_data.get("code")

    # Like "*Korea*"

    # E Ticket
    cursor.execute("""  SELECT `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura`  FROM FACTURA_ENCABEZADO 
                        WHERE `Fenc_TiqueteElect` = '1' AND `Fenc_Resultado` = 0 AND 
                        Fenc_EstadoProceso = 1 AND `Par_Cod_Emp` = ? AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' 
                         AND Fenc_Fecha_Factura > #7/1/2020#""", (str(user_code),))

    tickets_to_send = cursor.fetchall()

    # E Bill
    cursor.execute("""  SELECT `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura` FROM FACTURA_ENCABEZADO 
                        WHERE `Fenc_TiqueteElect` = '2' AND `Fenc_Resultado` = 0 AND 
                        Fenc_EstadoProceso = 1 AND `Par_Cod_Emp` = ? AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' 
                         AND Fenc_Fecha_Factura > #7/1/2020#""", (str(user_code),))

    bills_to_send = cursor.fetchall()

    cursor.execute("""SELECT `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 1 AND Fenc_EstadoProceso = 1 AND `Par_Cod_Emp` = ? """, (str(user_code),))

    credit_to_send = cursor.fetchall()

    cursor.execute("""SELECT `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 2 AND Fenc_EstadoProceso = 1 AND `Par_Cod_Emp` = ? """, (str(user_code),))

    debit_to_send = cursor.fetchall()

    for ticket in tickets_to_send:
        if send_ticket_xml(ticket, user_data):
            cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_EstadoProceso = 2 
            WHERE Fenc_ConsecutivoNumerico = ? """, (str(ticket[0]),))
            conn.commit()
            print(
                "Archivo {}.xml enviado al servidor de Hacienda".format(ticket[0]))
        else:
            print("Error en tiquete: {}".format(ticket[0]))

    for bill in bills_to_send:
        if send_bill_xml(bill, user_data):
            cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_EstadoProceso = 2
                WHERE Fenc_ConsecutivoNumerico = ? """, (str(bill[0]),))
            conn.commit()
            print(
                "Archivo {}.xml enviado al servidor de Hacienda".format(bill[0]))
        else:
            print("Error en factura: {}".format(bill[0]))

    for credit in credit_to_send:
        if send_credit_xml(credit, user_data):
            cursor.execute(""" UPDATE `Encab_NDCFact` SET Fenc_EstadoProceso = 2
            WHERE Fenc_ConsecutivoNumerico = ? """, (str(credit[0]),))
            conn.commit()
            print(
                "Archivo {}.xml enviado al servidor de Hacienda".format(credit[0]))
        else:
            print("Error en nota de credito: {}".format(credit[0]))

    for debit in debit_to_send:
        if send_debit_xml(credit, user_data):
            cursor.execute(""" UPDATE `Encab_NDCFact` SET Fenc_EstadoProceso = 2
            WHERE Fenc_ConsecutivoNumerico = ? """, (str(debit[0]),))
            conn.commit()
            print(
                "Archivo {}.xml enviado al servidor de Hacienda".format(debit[0]))
        else:
            print("Error en nota de debito: {}".format(debit[0]))


def get_user_parameters():
    user_list = []
    query_string = """  SELECT Par_Cod_Emp, Par_Nomb_Empresa, Par_RepLegal, Par_TipoCedula, Par_Cedula,
                        Par_Telefono1, Par_Correo, PAR_Provincia, PAR_Canton, PAR_Distrito,
                        PAR_Barrio, Par_Direccion, PAR_Pin, PAR_Acceso, PAR_Contrasena FROM PARAMETROS"""
    cursor.execute(query_string)
    result = cursor.fetchall()
    for line in result:
        user_data = {"code": line[0], "store_name": line[1], "registered_name": line[2], "id_type": line[3],
                     "id_number": line[4], "phone": line[5], "email": line[6], "province": line[7],
                     "canton": line[8], "district": line[9], "street": line[10], "address": line[11], "pin": line[12],
                     "access": line[13], "password": line[14]}
        user_list.append(user_data)
    return user_list


def get_simple_datetime():
    timezone = datetime.timezone(datetime.timedelta(hours=-6))
    current_datetime = datetime.datetime.now(timezone)
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def start_function():
    print("\n************\n{}\nIniciando envio de documentos a Hacienda\n".format(get_simple_datetime()))
    user_data = get_user_parameters()
    for element in user_data:
        get_to_send_data(element)


start_function()

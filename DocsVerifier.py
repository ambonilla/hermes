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


conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\PUNTOVENTA\\ANDROMEDA.accdb;')
cursor = conn.cursor()
base_path = "/PUNTOVENTA/Hermes/Documentos"


def oauth_decode(data):
    new_data = data.decode("utf-8", "strict")
    return json.loads(new_data)


def verify_data(user_data, doc_key):

    result_list = ["aceptado", "rechazado", "procesando", "recibido"]

    

    service = OAuth2Service(name="production",
                            client_id="api-prod",
                            client_secret="",
                            access_token_url="https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token")

    data = {'grant_type': 'password',
            'username': '{}@prod.comprobanteselectronicos.go.cr'.format(user_data.get("access")),
            'password': '{}'.format(user_data.get("password"))}

    url_send = "https://api.comprobanteselectronicos.go.cr/recepcion/v1/recepcion/{}".format(doc_key)


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

    url_send = "https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/recepcion/{}".format(doc_key)

    """

    session = service.get_auth_session(data=data, decoder=oauth_decode)

    access_token = session.access_token

    
    headers = {"Authorization": "Bearer " + access_token}

    print(url_send)

    response = requests.get(url_send, headers=headers)
    print("Respuesta: ", response.text)
    if len(response.text) > 0:
      if not "error" in response.text:
        result = json.loads(response.text)
        state = result["ind-estado"]

        if "respuesta-xml" in result:
            xml_data = result["respuesta-xml"]
            state_index = 0
            if state in result_list:
                state_index = result_list.index(state) + 1

                return {"response": base64.b64decode(xml_data).decode('utf-8'), "status": state_index, "result": True}
    else:
        cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_EstadoProceso = 1 WHERE Fenc_ClaveNumerica = ? """, ( str(doc_key),))
        conn.commit()
    return {"response": "", "status": 0, "result": False}


def get_to_verify_data(user_data):

    user_code = user_data.get("code")

    # Like "*Korea*"

    # E Ticket
    cursor.execute("""  SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura` 
     FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '1' AND `Fenc_Resultado` = 0 AND 
                        Fenc_EstadoProceso = 2 AND `Par_Cod_Emp` = ? AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' 
                         AND Fenc_Fecha_Factura > #7/1/2020# """, (str(user_code),))

    tickets_to_send = cursor.fetchall()

    # E Bill
    cursor.execute("""  SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura`  
    FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '2' AND `Fenc_Resultado` = 0 AND 
                        Fenc_EstadoProceso = 2 AND `Par_Cod_Emp` = ? AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' 
                         AND  Fenc_Fecha_Factura > #7/1/2020# """, (str(user_code),))

    bills_to_send = cursor.fetchall()

    # Credit Note
    cursor.execute(""" SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` 
    FROM Encab_NDCFact WHERE `JUS_TipoNota` = 1  AND Fenc_EstadoProceso = 2 AND 
    `Par_Cod_Emp` = ? """, (str(user_code),))

    credit_to_send = cursor.fetchall()


    # Credit Note
    cursor.execute("""SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, 
    `NENC_FechaNota` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 2 AND 
    Fenc_EstadoProceso = 2 AND `Par_Cod_Emp` = ? """, (str(user_code),))

    debit_to_send = cursor.fetchall()

    for ticket in tickets_to_send:
        output_dictionary = verify_data(user_data, ticket[0])
        if output_dictionary.get("result"):
            cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_EstadoProceso = 3, Fenc_Resultado = ?  
            WHERE Fenc_ConsecutivoNumerico = ? """, (str(output_dictionary.get("status")), str(ticket[1]),))
            conn.commit()
            directory_path = "{}/{}/Tiquetes/{}/".format(base_path, user_data.get("id_number"),
                                                         ticket[2].strftime('%Y-%m-%d'))
            file_name = "mh-{}.xml".format(str(ticket[1]).strip())

            file_output = open('{}{}'.format(directory_path, file_name), 'w', encoding='utf-8')
            file_output.write(output_dictionary.get("response"))
            file_output.close()
            print("Respuesta {} recibida de Hacienda".format(file_name))
        else:
            print("Error en tiquete: {}".format(ticket[0]))

    for bill in bills_to_send:
        output_dictionary = verify_data(user_data, bill[0])
        if output_dictionary.get("result"):
            cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_EstadoProceso = 3, Fenc_Resultado = ? 
                WHERE Fenc_ConsecutivoNumerico = ? """, (str(output_dictionary.get("status")), str(bill[1]),))
            conn.commit()
            directory_path = "{}/{}/Facturas/{}/".format(base_path, user_data.get("id_number"),
                                                         bill[2].strftime('%Y-%m-%d'))
            file_name = "mh-{}.xml".format(str(bill[1]).strip())

            file_output = open('{}{}'.format(directory_path, file_name), 'w', encoding='utf-8')
            file_output.write(output_dictionary.get("response"))
            file_output.close()

            print("Respuesta {} recibida de Hacienda".format(file_name))
        else:
            print("Error en factura: {}".format(bill[0]))

    for credit in credit_to_send:
        output_dictionary = verify_data(user_data, credit[0])
        if output_dictionary.get("result"):

            cursor.execute("""  UPDATE `Encab_NDCFact` SET Fenc_EstadoProceso = 3, Fenc_Resultado = ?
            WHERE Fenc_ConsecutivoNumerico = ?  """, (str(output_dictionary.get("status")), str(credit[1]),))
            conn.commit()
            directory_path = "{}/{}/Notas de Credito/{}/".format(base_path, user_data.get("id_number"),
                                                   credit[2].strftime('%Y-%m-%d'))
            file_name = "mh-{}.xml".format(str(credit[1]).strip())

            file_output = open('{}{}'.format(directory_path, file_name), 'w', encoding='utf-8')
            file_output.write(output_dictionary.get("response"))
            file_output.close()

            print("Respuesta {} recibida de Hacienda".format(file_name))
        else:
            print("Error en NC: {}".format(credit[0]))

    for debit in debit_to_send:
        output_dictionary = verify_data(user_data, debit[0])
        if output_dictionary.get("result"):

            cursor.execute("""  UPDATE `Encab_NDCFact` SET Fenc_EstadoProceso = 3, Fenc_Resultado = ?
            WHERE Fenc_ConsecutivoNumerico = ?  """, (str(output_dictionary.get("status")), str(debit[1]),))
            conn.commit()
            directory_path = "{}/{}/ND/{}/".format(base_path, user_data.get("id_number"),
                                                   debit[2].strftime('%Y-%m-%d'))
            file_name = "mh-{}.xml".format(str(debit[1]).strip())

            file_output = open('{}{}'.format(directory_path, file_name), 'w', encoding='utf-8')
            file_output.write(output_dictionary.get("response"))
            file_output.close()

            print("Respuesta {} recibida de Hacienda".format(file_name))
        else:
            print("Error en ND: {}".format(debit[0]))


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
    print("\n************\n{}\nIniciando verificacion de documentos\n".format(get_simple_datetime()))
    user_data = get_user_parameters()
    for element in user_data:
        get_to_verify_data(element)

start_function()

import pyodbc
import os
import subprocess
import datetime
import time
import base64
import json
import xmltodict
import requests
from random import randint


conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\PUNTOVENTA\\ANDROMEDA.accdb;')
cursor = conn.cursor()
base_path = "/PUNTOVENTA/Hermes/Documentos"


def send_mail_request(sender_name, sender_email, receiver_name,
                      receiver_email, edoc_64, mh_64, pdf_64,
                      doc_name, doc_subject, status, doc_type):
    body = {"sender": sender_name,
            "sender_email": sender_email,
            "receiver": receiver_name,
            "receiver_email": receiver_email,
            "pdf": pdf_64,
            "edoc": edoc_64,
            "mh": mh_64,
            "file_name": doc_name,
            "mail_subject": doc_subject,
            "document_status": status,
            "document_type": doc_type}

    send_url = "http://andromedasistemas.net/andromeda_mail_sender.php"
    json_data = json.dumps(body).encode('utf-8')
    time.sleep(randint(10, 25))

    if True:

        # print(send_url)
	    # print(json_data)        
        response = requests.post(send_url, json_data, headers={'content-type': 'application/json'})

        print("Correo {} enviado".format(doc_name))        
		#print(response)
        #print(response.text)
        return json.loads(response.text)

    else:
        print("Documento {} no enviado.\nReintentando en próximo ciclo".format(doc_name))
        return {'status': '1'}


def send_data(user_data, doc_key, doc_consecutive, doc_date, doc_type):
    if doc_type == 1:
        element = "NotaCreditoElectronica"
        doc_type = "Nota de Crédito Electrónica"
        directory_path = "{}/{}/Notas de Credito/{}/".format(base_path, user_data.get("id_number"),
                                                     doc_date.strftime('%Y-%m-%d'))
    elif doc_type == 2:
        element = "NotaDebitoElectronica"
        doc_type = "Nota de Débito Electrónica"
        directory_path = "{}/{}/ND/{}/".format(base_path, user_data.get("id_number"),
                                                     doc_date.strftime('%Y-%m-%d'))
    else:
        element = "FacturaElectronica"
        doc_type = "Factura Electrónica"
        directory_path = "{}/{}/Facturas/{}/".format(base_path, user_data.get("id_number"),
                                                     doc_date.strftime('%Y-%m-%d'))

    response_file_name = "mh-{}.xml".format(str(doc_consecutive).strip())
    doc_file_name = "{}.xml".format(str(doc_consecutive).strip())
    pdf_file_name = "{}.pdf".format(str(doc_consecutive).strip())

    if not os.path.isdir('{}'.format(directory_path)):
        return False
    elif not os.path.isfile('{}{}'.format(directory_path, doc_file_name)):
        print("{} no existe.".format(doc_file_name))
        return False
    elif not os.path.isfile('{}{}'.format(directory_path, response_file_name)):
        print("{} no existe.".format(response_file_name))
        return False
    elif not os.path.isfile('{}{}'.format(directory_path, pdf_file_name)):
        print("{} no existe.".format(pdf_file_name))
        return False

    else:
        file_pointer = open("{}{}".format(directory_path, doc_file_name.strip()), 'r', encoding='utf-8')
        edoc_data = file_pointer.read()
        file_pointer.close()
        file_pointer = open("{}{}".format(directory_path, response_file_name.strip()), 'r', encoding='utf-8')
        mh_data = file_pointer.read()
        file_pointer.close()
        file_pointer = open("{}{}".format(directory_path, pdf_file_name.strip()), 'rb')
        pdf_data = file_pointer.read()
        file_pointer.close()

        edoc_64 = base64.b64encode(edoc_data.encode('utf-8')).decode('utf-8')
        mh_64 = base64.b64encode(mh_data.encode('utf-8')).decode('utf-8')
        pdf_64 = base64.b64encode(pdf_data).decode('utf-8')

        dictionary_data = xmltodict.parse(edoc_data, encoding="utf-8")
        dictionary_data = dictionary_data[element]
        sender_email = dictionary_data["Emisor"]["CorreoElectronico"]
        receiver_data = dictionary_data["Receptor"]
        if "CorreoElectronico" in receiver_data:
            receiver_email = dictionary_data["Receptor"]["CorreoElectronico"]
            sender_name = dictionary_data["Emisor"]["Nombre"]
            receiver_name = dictionary_data["Receptor"]["Nombre"]

            result_data = xmltodict.parse(mh_data, encoding="utf-8")
            result = result_data["MensajeHacienda"]["Mensaje"]
            if int(result) == 1:
                result = "ACEPTADO"
            elif int(result) == 2:
                result = "ACEPTADO PARCIALMENTE"
            elif int(result) == 3:
                result = "RECHAZADO"
            #print("********\n",sender_name.strip())
            #print(sender_email.strip())
            #print(receiver_name.strip())
            #print(receiver_email.strip())
            #print(pdf_64)
            print("Sending data")
            print("De: ", sender_name.strip())
            print("Email: ", sender_email.strip())
            print("Para: ", receiver_name.strip())
            print("Email: ", receiver_email.strip())

            mail_result = send_mail_request(sender_name.strip(), sender_email.strip(), receiver_name.strip(),
                                            receiver_email.strip(), edoc_64, mh_64, pdf_64, doc_consecutive, doc_key,
                                            result, doc_type)
            print("mail result: ", mail_result.get('status'))
            return mail_result.get('status') == 0
        else:
            return True


def get_to_send_mail_data(user_data):

    user_code = user_data.get("code")

    # E Bill
    cursor.execute("""  SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura` 
                        FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '2' AND `Fenc_Resultado` > 0 AND 
                        Fenc_EstadoProceso = 3 AND Fenc_EnviadoCorreo = 0 AND `Par_Cod_Emp` = ?""", (str(user_code),))

    bills_to_mail = cursor.fetchall()

    # Credit Note
    cursor.execute("""  SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 1
     AND `Fenc_Resultado` > 0  AND Fenc_EstadoProceso = 3 AND 
     Fenc_EnviadoCorreo = 0 AND `Par_Cod_Emp` = ?""", (str(user_code),))

    credit_to_mail = cursor.fetchall()

    # Debit Note
    cursor.execute("""  SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 2
     AND `Fenc_Resultado` > 0  AND Fenc_EstadoProceso = 3 AND 
     Fenc_EnviadoCorreo = 0 AND `Par_Cod_Emp` = ?""", (str(user_code),))

    debit_to_mail = cursor.fetchall()

    for bill in bills_to_mail:
        print(bill[0])
        output_dictionary = send_data(user_data, bill[0], bill[1], bill[2], 0)
        # print(output_dictionary)
        if output_dictionary:
            cursor.execute("""  UPDATE FACTURA_ENCABEZADO SET Fenc_EnviadoCorreo = 1 WHERE 
                                Fenc_ConsecutivoNumerico = ? """, (str(bill[1]),))
            conn.commit()
        else:
            print("Error de envío en factura: {}".format(bill[0]))

    for credit in credit_to_mail:
        print(credit)
        output_dictionary = send_data(user_data, credit[0], credit[1], credit[2], 1)
        # print(output_dictionary)
        if output_dictionary:
            cursor.execute("""  UPDATE Encab_NDCFact SET Fenc_EnviadoCorreo = 1 WHERE 
                                Fenc_ConsecutivoNumerico = ? """, (str(credit[1]),))
            conn.commit()
        else:
            print("Error de envío en nota de crédito: {}".format(credit[0]))

    for debit in debit_to_mail:
        print(debit[0])
        output_dictionary = send_data(user_data, debit[0], debit[1], debit[2], 1)
        # print(output_dictionary)
        if output_dictionary:
            cursor.execute("""  UPDATE Encab_NDCFact SET Fenc_EnviadoCorreo = 1 WHERE 
                                Fenc_ConsecutivoNumerico = ? """, (str(debit[1]),))
            conn.commit()
        else:
            print("Error de envío en nota de débito: {}".format(debit[0]))


def get_user_parameters():
    user_list = []
    query_string = """  SELECT Par_Cod_Emp, Par_Nomb_Empresa, Par_RepLegal, Par_TipoCedula, Par_Cedula,
                        Par_Telefono1, Par_Correo, PAR_Provincia, PAR_Canton, PAR_Distrito,
                        PAR_Barrio, Par_Direccion, PAR_Pin, PAR_Acceso, PAR_Contrasena, PAR_CorreoContrasena 
                        FROM PARAMETROS """
    cursor.execute(query_string)
    result = cursor.fetchall()
    for line in result:
        user_data = {"code": line[0], "store_name": line[1], "registered_name": line[2], "id_type": line[3],
                     "id_number": line[4], "phone": line[5], "email": line[6], "province": line[7],
                     "canton": line[8], "district": line[9], "street": line[10], "address": line[11], "pin": line[12],
                     "access": line[13], "password": line[14], "email_password": line[15]}
        user_list.append(user_data)
    return user_list


def get_simple_datetime():
    timezone = datetime.timezone(datetime.timedelta(hours=-6))
    current_datetime = datetime.datetime.now(timezone)
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def start_function():
    #cursor.execute("""  UPDATE Encab_NDCFact SET Fenc_EnviadoCorreo = 0 WHERE  Fenc_Numero = 4349 or  Fenc_Numero = 4348 or  Fenc_Numero = 4337 or  Fenc_Numero = 4281 or Fenc_Numero = 4387 or Fenc_Numero = 4369 or Fenc_Numero = 4134 or Fenc_Numero = 4017 or Fenc_Numero = 4011 or Fenc_Numero = 4402 """)
    #conn.commit()
    print("\n************\n{}\nIniciando envio de correos\n".format(get_simple_datetime()))
    user_data = get_user_parameters()
    for element in user_data:
        get_to_send_mail_data(element)

start_function()
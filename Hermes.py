from UserParameters import UserParameters
from ElectronicDocument import ElectronicDocument
import time
import datetime


def get_simple_datetime():
    timezone = datetime.timezone(datetime.timedelta(hours=-6))
    current_datetime = datetime.datetime.now(timezone)
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def get_to_sign_data(user_data):

    electronic_documents = ElectronicDocument(user_data.get("code"))
    electronic_documents.get_etickets()
    electronic_documents.get_ebills()
    electronic_documents.get_credit_notes()
    electronic_documents.prepare_docs(user_data)
    
    #electronic_documents.get_debit_notes()
    #

    #electronic_documents.create_xml(user_data)

def separate_user_address(user_data):
    user_data['id_number'] = user_data['id_number'].replace('-', '')
    user_data['phone'] = user_data['phone'].replace('-', '')
    user_data['codigo_provincia'] = user_data['province'][ :user_data['province'].find(' ')]
    user_data['provincia'] = user_data['province'][user_data['province'].find('-') + 2:]
    user_data['codigo_canton'] = user_data['canton'][ :user_data['canton'].find(' ')]
    user_data['canton'] = user_data['canton'][user_data['canton'].find('-') + 2:]
    user_data['codigo_distrito'] = user_data['district'][ :user_data['district'].find(' ')]
    user_data['distrito'] = user_data['district'][user_data['district'].find('-') + 2:]
    return user_data

def start_function():
    while True:
        print(f"\n************\n{get_simple_datetime()}\nIniciando firma de documentos\n")
        current_users = UserParameters()
        connection_message, result, query_output = current_users.get_user_parameters()
        print(connection_message)

        if result:
            for element in query_output:
                get_to_sign_data(separate_user_address(element))
        else:
            print(query_output)

        import DocsSender
        import DocsVerifier
        import PdfCreator
        import DocsMailSender

        print("Ciclo Finalizado")

        time.sleep(300)


if __name__ == "__main__":
    start_function()

from UserParameters import UserParameters
from ElectronicDocument import ElectronicDocument


def get_simple_datetime():
    timezone = datetime.timezone(datetime.timedelta(hours=-6))
    current_datetime = datetime.datetime.now(timezone)
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def get_to_sign_data(user_data):
    electronic_documents = ElectronicDocument(user_data.get("code"))
    electronic_documents.get_etickets()
    electronic_documents.get_ebills()
    electronic_documents.get_debit_notes()
    electronic_documents.get_credit_notes()


def start_function():
    print(f"\n************\n{get_simple_datetime()}\nIniciando firma de documentos\n")
    current_users = UserParameters()
    connection_message, result, query_output = current_users.get_user_parameters()
    print(connection_message)

    if result:
        for element in query_output:
            get_to_sign_data(element)

    else:
        print(query_output)


if __name__ == "main":
    start_function()

from AccessConnection import AccessConnection

class Client:

    def __init__(self, client_code):
        self.client_code = client_code
        self.current_connection = None

    def get_client_data(self):
        self.current_connection = AccessConnection()

        query_string = """  SELECT `CxC_TipoCedula`, `CxC_Numero_Cedula`, `CxC_Nombre`, `CxC_Telef1`,
        `CxC_CorreoElectronico`, CxC_Provincia, CxC_Canton, CxC_Distrito, CxC_Barrio , CxC_Direccion 
        FROM `CLIENTES` WHERE `CxC_Cod_Cliente` = ?"""
        
        if self.current_connection.status:
            query_output, result = current_connection.run_query_fetch_single(query_string, (str(self.client_code), ))
            
            if result:
                if len(query_output) > 0:
                    return {"client_id_type": query_output[0], "client_id_number": query_output[1], 
                    "client_name": query_output[2], "client_phone": query_output[3], "client_email": query_output[4], 
                    "client_province": query_output[5], "client_canton": query_output[6], 
                    "client_district": query_output[7], "client_street": query_output[8],
                    "client_signals": query_output[9]}
                else:
                    print(query_output)
                    return {}
            else:
                print(query_output)
                return {}
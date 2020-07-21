from AccessConnection import AccessConnection

class Client:

    def __init__(self, client_code):
        self.client_code = client_code
        self.current_connection = None

    def remove_address_extra_data(self, address):
        return address[:address.find(" -")]

    def get_client_data(self):
        self.current_connection = AccessConnection()

        query_string = """  SELECT `CxC_TipoCedula`, `CxC_Numero_Cedula`, `CxC_Nombre`, `CxC_Telef1`,
        `CxC_CorreoElectronico`, CxC_Provincia, CxC_Canton, CxC_Distrito, CxC_Barrio , CxC_Direccion 
        FROM `CLIENTES` WHERE `CxC_Cod_Cliente` = ?"""
        
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query_fetch_single(query_string, (str(int(self.client_code)), ))
            
            if result:
                if len(query_output) > 0:
                    phone = query_output[3].replace("-","")    
                    
                    if len(query_output[9].strip()) > 0:
                        other_signals = query_output[9].strip()                
                    else:
                        other_signals = self.remove_address_extra_data(query_output[6])
                    return {"client_id_type": query_output[0], "client_id_number": query_output[1], 
                    "client_name": query_output[2].strip(), "client_phone": phone.strip(), 
                    "client_email": query_output[4].strip(), 
                    "client_province": self.remove_address_extra_data(query_output[5]), 
                    "client_canton": self.remove_address_extra_data(query_output[6]), 
                    "client_district": self.remove_address_extra_data(query_output[7]), "client_street": query_output[8],
                    "client_signals": other_signals}
                else:
                    print(query_output)
                    return {}
            else:
                print(query_output)
                return {}
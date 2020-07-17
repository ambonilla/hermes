from AccessConnection import AccessConnection

class UserParameters:

    def __init__(self):
        self.user_list = [] 
        self.current_connection = False       

    """
    Returns:
           Dictionary list with following keys:

           code
           store_name
           registered_name
           id_type
           id_number
           phone
           email
           province
           canton
           district
           street
           address
           pin
           activity_code

    """

    def get_user_parameters(self):
        query_string = """SELECT Par_Cod_Emp, Par_Nomb_Empresa, Par_RepLegal, Par_TipoCedula, Par_Cedula, 
        Par_Telefono1, Par_Correo, PAR_Provincia, PAR_Canton, PAR_Distrito,
        PAR_Barrio, Par_Direccion, PAR_Pin, PAR_Actividad FROM PARAMETROS"""        

        self.current_connection = AccessConnection()
        result = False
        query_output = ""
        
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(query_string)
            if result:
                for line in query_output:                    
                    self.user_list.append({"code": line[0], "store_name": line[1], "registered_name": line[2], 
                    "id_type": '{:02d}'.format(int(line[3])), "id_number": line[4], "phone": line[5], "email": line[6], 
                    "province": line[7], "canton": line[8], "district": line[9], "street": line[10], 
                    "address": line[11], "pin": line[12], "activity_code": line[13]})

                return self.current_connection.message, result, self.user_list

        else:
            return self.current_connection.message, result, query_output


        
            


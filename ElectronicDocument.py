from AccessConnection import AccessConnection
from Client import Client


class ElectronicDocument:

    def __init__(self, user_code):
        self.user_code = user_code
        self.etickets = []
        self.ebills = []
        self.credit_notes = []
        self.debit_notes = []
        self.current_connection = False

    def doc_reference(self, edoc_number):
        query_string = """SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Nomb_Cliente`, 
                        `Fenc_Fecha_Factura`, `Fenc_Observacion`, `Fenc_MontoEfectivo`, `Fenc_Monto_Tarjeta`, 
                        `Fenc_MontoCheque`, `Fenc_MontoDeposito`, `Fenc_Numero`, `Fenc_Cod_Cliente`, `Fenc_Tipo_Factura`,
                        `Fenc_Plazo`, `Fenc_PorServicioMesa` FROM FACTURA_ENCABEZADO WHERE `Fenc_Numero` = ? AND 
                        `Par_Cod_Emp` = ?"""
        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = current_connection.run_query_fetch_single(query_string, (str(edoc_number), self.user_code,))

            if result:
                if len(query_output) > 0:
                    return {'key': query_output[0], 'consecutive': query_output[1], 'client': query_output[2],
                    'doc_date': query_output[3], 'remarks': query_output[4], 'cash': query_output[5],
                    'card': query_output[6], 'check': query_output[7], 'transfer': query_output[8],
                    'doc_type': query_output[11], 'credit_time': query_output[12], 'service': query_output[13]}
                else:
                    return {}
            else:
                return {}

    def get_doc_lines(self, bill_number):
        lines = []
        query_string = """  SELECT `Art_Cod_Logico`, `DFA_Cantidad`, `DFA_PV_SinImp`, `DFA_Descuento`, `DFA_Porc_IV` 
    FROM DET_FACTURA WHERE `Fenc_Numero` = ?  """

        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = current_connection.run_query(query_string, (str(bill_number), ))
            
            if result:
                for row in query_output:
                    current_article = Article(row[0])
                    article_dictionary = current_article.get_article_data()
                    lines.append({'code': row[0], 'quantity': row[1], 'price': row[2], 'discount': row[3],
                    'tax': row[4], 'description': article_dictionary.get("description"),
                    'unit': article_dictionary.get("unit"), 'iva_code': article_dictionary.get("iva_code"),
                    'iva_tarif': article_dictionary.get("iva_tarif"),
                    'iva_percentage': article_dictionary.get("iva_percentage")})
                    
        return lines

    def doc_nc_lines(bill_number):
        lines = []
        query_string = """  SELECT `Art_Cod_Logico`, `DFA_Cantidad`, `DFA_PV_SinImp`, `DFA_Descuento`, 
        `DFA_Porc_IV` FROM DET_NDFact WHERE `NENC_ConsLogico` = ? """
        
        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = current_connection.run_query(query_string, (str(bill_number),))

            if result:
                for row in query_output:
                    current_article = Article(row[0])
                    article_dictionary = current_article.get_article_data()
                    lines.append({'code': row[0], 'quantity': row[1], 'price': row[2], 'discount': row[3],
                    'tax': row[4], 'description': article_dictionary.get("description"),
                    'unit': article_dictionary.get("unit"), 'iva_code': article_dictionary.get("iva_code"),
                    'iva_tarif': article_dictionary.get("iva_tarif"),
                    'iva_percentage': article_dictionary.get("iva_percentage")})
                    
        return lines

    def docs_to_sign(self, query_result):
        output_list = []
        for row in query_result:
            current_client = Client(row[10])
            output_list.append({'key': row[0], 'consecutive': row[1], 'client': row[2],
            'doc_date': row[3], 'remarks': row[4], 'cash': row[5],
            'card': row[6], 'check': row[7], 'transfer': row[8],
            'number': row[9], 
            'lines': self.doc_lines(row[9]), 
            'client_data': current_client.get_client_data(),
            'doc_type': row[11], 'credit_time': row[12], 'service': row[13]})
            
        return output_list        


    def notes_to_sign(self, query_result):
        sign_list = []
        for row in query_result:
            current_client = Client(row[5])
            sign_list.append({'key': row[0], 'consecutive': row[1], 
            'doc_date': row[2], 'remarks': row[3], 'number': row[4], 
            'client_data': current_client.get_client_data()),
            'exempt': row[6], 
            'lines': self.doc_nc_lines(row[7]), 
            'reason': row[8],
            'reference_data': self.doc_reference(row[9])})
            
        return sign_list


    def get_etickets(self):
        query_string = """SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Nomb_Cliente`, 
        `Fenc_Fecha_Factura`, `Fenc_Observacion`, `Fenc_MontoEfectivo`, `Fenc_Monto_Tarjeta`, 
        `Fenc_MontoCheque`, `Fenc_MontoDeposito`, `Fenc_Numero`, `Fenc_Cod_Cliente`, `Fenc_Tipo_Factura`,
        `Fenc_Plazo`, `Fenc_PorServicioMesa` FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '1' 
        AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ?"""

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = current_connection.run_query(query_string, (str(self.user_code), ))
            if result:
                self.etickets = self.docs_to_sign(query_output)
            else:
                print(query_output)


    def get_ebills(self):
        query_string = """SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Nomb_Cliente`, 
        `Fenc_Fecha_Factura`, `Fenc_Observacion`, `Fenc_MontoEfectivo`, `Fenc_Monto_Tarjeta`, 
        `Fenc_MontoCheque`, `Fenc_MontoDeposito`, `Fenc_Numero`, `Fenc_Cod_Cliente`, `Fenc_Tipo_Factura`,
        `Fenc_Plazo`, `Fenc_PorServicioMesa` FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '2' 
        AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ?"""

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = current_connection.run_query(query_string, (str(self.user_code), ))
            if result:
                self.ebills = self.docs_to_sign(query_output)
            else:
                print(query_output)

    def get_debit_notes(self):
        query_string = """SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`,  
                        `NENC_FechaNota`, `NENC_Observacion`, 
                        `NENC_Numero`, `Fenc_Cod_Cliente`, `Fenc_Exonerada`,
                        `NENC_ConsLogico`, `JUS_Clase`, `Fenc_Numero` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 2 
                        AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ?"""

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = current_connection.run_query(query_string, (str(self.user_code), ))
            if result:
                self.debit_notes = self.notes_to_sign(query_output)
            else:
                print(query_output)

    def get_credit_notes(self):
        query_string = """SELECT `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`,  
                        `NENC_FechaNota`, `NENC_Observacion`, 
                        `NENC_Numero`, `Fenc_Cod_Cliente`, `Fenc_Exonerada`,
                        `NENC_ConsLogico`, `JUS_Clase`, `Fenc_Numero` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 1 
                        AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ?"""
        
        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = current_connection.run_query(query_string, (str(self.user_code), ))
            if result:
                self.credit_notes = self.notes_to_sign(query_output)
            else:
                print(query_output)                        
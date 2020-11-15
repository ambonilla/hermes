from AccessConnection import AccessConnection


class Article:

    def __init__(self, article_code):
        self.article_code = article_code
        self.current_connection = None

    def get_article_unit(self, article_unit_code):
        
        self.current_connection = AccessConnection()

        query_string = """SELECT `UND_Desc_Unidad` FROM UNIDADES WHERE `UND_Cod_Logico` = ? """
        
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query_fetch_single(query_string, (str(article_unit_code),))

            if result:
                return query_output[0]
                
    def get_tax_value(self, tax_code, tax_code_tariff):
        
        self.current_connection = AccessConnection()

        query_string = """SELECT `TxI_Valor` FROM Tarifas WHERE `TxI_CodImpuesto` = ? AND 
        `TxI_CodTarifa` = ? """ 
        
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query_fetch_single(query_string, 
            (str(tax_code), str(tax_code_tariff),))
            
            if result:
                return query_output[0]

    def get_article_data(self):

        self.current_connection = AccessConnection()

        query_string = """SELECT `Art_Nombre_Articulo`, `UND_Cod_Logico`, `Art_CodIVA`, `Art_TarifaIVA`, `Art_CodArtHacienda` 
        FROM ARTICULOS WHERE `Art_Cod_Logico` = ? """

        if self.current_connection.status:
            query_output, result = self.current_connection.run_query_fetch_single(query_string, (str(self.article_code), ))

            if result:
                return {"description": query_output[0], "unit": self.get_article_unit(query_output[1]),
                "iva_code": query_output[2], "iva_tarif": query_output[3], 
                "iva_percentage": self.get_tax_value(query_output[2], query_output[3]),
                "cabys":query_output[4]}

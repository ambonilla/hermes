import pyodbc


class AccessConnection:

    def __init__(self, access_path="C:\\PUNTOVENTA\\ANDROMEDA.accdb"):
        try:
            self.conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ={};'.format(access_path))
            self.cursor = conn.cursor()
            self.message = "Conexion Realizada"
            self.status = True
        except:
            self.message = "Base de Datos no Encontrada"
            self.status = False

    def run_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            query_output = self.cursor.fetchall()            
            result = True
        except:
            query_output = "Error en ejecucion de {query} con valores:\n{values}"
            result = False
        finally:
            self.conn.close()
            return query_output, result

    def run_query_fetch_single(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            query_output = self.cursor.fetchone()            
            result = True
        except:
            query_output = "Error en ejecucion de {query} con valores:\n{values}"
            result = False
        finally:
            self.conn.close()
            return query_output, result
        

    
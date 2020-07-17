import pyodbc


class AccessConnection:

    def __init__(self):
        try:
            connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\PUNTOVENTA\\ANDROMEDA.accdb;'
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
            self.message = "Conexion Realizada"
            self.status = True
        except:
            self.message = "Base de Datos no Encontrada"
            self.status = False

    def update_query(self, query, values=()):
        try:
            self.cursor.execute(query, values)
            query_output = self.cursor.commit()
            result = True
        except:
            query_output = f"Error en ejecucion de {query} con valores:\n{values}"
            result = False
        finally:
            self.conn.close()
            return query_output, result

    def run_query(self, query, values=()):
        try:
            self.cursor.execute(query, values)
            query_output = self.cursor.fetchall()
            result = True
        except:
            query_output = f"Error en ejecucion de {query} con valores:\n{values}"
            result = False
        finally:
            self.conn.close()
            return query_output, result

    def run_query_fetch_single(self, query, values=()):
        try:
            self.cursor.execute(query, values)
            query_output = self.cursor.fetchone()
            result = True
        except:
            query_output = f"Error en ejecucion de {query} con valores:\n{values}"
            result = False
        finally:
            self.conn.close()
            return query_output, result

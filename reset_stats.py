import pyodbc

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\PUNTOVENTA\\ANDROMEDA.accdb;')
cursor = conn.cursor()
base_path = "/PUNTOVENTA/Hermes/Documentos"

cursor.execute("""  UPDATE `Encab_NDCFact` SET Fenc_Pdf = 0 WHERE NENC_FechaNota > 2/7/2020  """)
conn.commit()

cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_Pdf = 0 WHERE Fenc_Fecha_Factura > 2/7/2020 """)
conn.commit()            

#cursor.execute("""  UPDATE `Encab_NDCFact` SET Fenc_EstadoProceso = 0, Fenc_Resultado = 0, Fenc_Pdf = 0, Fenc_EnviadoCorreo = 0 """)
#conn.commit()

#cursor.execute(""" UPDATE FACTURA_ENCABEZADO SET Fenc_EstadoProceso = 0, Fenc_Resultado = 0, Fenc_Pdf = 0, Fenc_EnviadoCorreo = 0""")
#conn.commit()            
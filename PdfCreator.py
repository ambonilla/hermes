import qrcode
import pyodbc
import os
import xmltodict
import platform
import subprocess
import datetime


conn = pyodbc.connect(
    r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\PUNTOVENTA\\ANDROMEDA.accdb;')
cursor = conn.cursor()
base_path = "/PUNTOVENTA/Hermes/Documentos"


def filter_character(string=""):
    if string:
        if "&amp;" in string:
            string = string.replace("&amp;", "&")
        if "&apos;" in string:
            string = string.replace("&apos;", "'")
        if "&lt;" in string:
            string = string.replace("&lt;", "<")
        if "&gt;" in string:
            string = string.replace("&gt;", ">")
        if "&quot;" in string:
            string = string.replace("&quot;", '"')
    return string


def get_current_os():
    current_platform = platform.system()
    if current_platform == 'Linux':
        return 0
    elif current_platform == 'Windows':
        return 1
    elif current_platform == 'Darwin':
        return 2


def html_creator(bill_key, user_data, doc_data, client, bill_remarks, subtotal, discount, main_total,
                 tax_total, service_total, gravado, exento, exonerado, venta_neta):

    html_header = """
    <html >
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <style>
        body{
            margin: 0;
            padding: 0;
        }
        .page_div {
            width:210mm;
            height:277mm;
            margin-left:auto;
            margin-right:auto;
        }
        h3{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            padding:0;
            margin:0;
        }
        p{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
        }
        blockquote {
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
        }
        pre {
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
        }
        table{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            border-collapse: collapse;
        }
        .quotation-table{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            align: center;
            width: 100%;
            border-radius:10px;
        }
        .quote-number{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            float:right;
            align:center;
            width:40%;
            border-radius:10px;
            border: 1px solid black;
        }
        .center-row{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            align: center;
        }
        .header-left{
            width: 50%;
            float: left;
            align: center;
        }
        .header-right{
            width: 50%;
            float: left;
        }
        th{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            background-color: #000000;
            color: #ffffff;
            align: center;
        }
        .article-column{
            width: 30%;
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
        }
        .table-cell{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            border-top: 1px solid black;
            border-right: 1px solid black;
            border-left: 1px solid black;
            border-bottom: 1px solid black;
        }
        .last-cell{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            border-right: 1px solid black;
            border-left: 1px solid black;
            border-bottom: 1px solid black;
        }
        .table-total{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            border-top: 1px solid black;
            border-bottom: 1px solid black;
            border-right: 1px solid black;
        }
        .observations{
            font-family: Calibri, Candara, Segoe, 'Segoe UI', Optima, Arial, sans-serif;
            border: 1px solid black;
            border-radius:10px;
        }
    </style>
</head>
"""
    img = qrcode.make('{}'.format(bill_key))
    img.save("/PUNTOVENTA/Hermes/Apps/img/{}.png".format(bill_key))

    if get_current_os() == 1:
        logo_path = "C:\\PUNTOVENTA\\Hermes\\Apps\\img\\logo.png"
        qr_path = "C:\\PUNTOVENTA\\Hermes\\Apps\\img\\{}.png".format(bill_key)
    else:
        logo_path = "/PUNTOVENTA/Hermes/Apps/img/logo.png"
        qr_path = "/PUNTOVENTA/Hermes/Apps/img/{}.png".format(bill_key)

    html_upper_body_sender = """
<body bgcolor="#ffffff">
    <div class="page_div">
        <br />
        <br />
        <br />
        <div align="center">
            <table>
                <tr>
                    <td align="left" width="20%">
                        <img src="file:///{}"  width="128" height="128" align="left">
                    </td>
                    <td align="center" width="60%">
                        <h3>{}</h3>
                        {}<br/>
                        {}<br/>
                        {}<br/>
                        {}<br/>
                    </td>
                    <td align="right" width="20%">                        
                    </td>
                </tr>
            </table>
        </div>
""".format(logo_path, filter_character(user_data.get("store_name")), user_data.get("id_number"), user_data.get("phone"),
           filter_character(user_data.get("email")), filter_character(user_data.get("address")))

    html_upper_body_doc_data = """
    <div>
        <table width="100%">
            <tr>
                <td width="40%" align="left">
                    <table class="quotation-table">
                        <tr><td align="right"><b>Cliente:</b></td><td>{}</td></tr>                    
                        <tr><td align="right"><b>Cédula:</b></td><td>{}</td></tr>
                        <tr><td align="right"><b>Email:</b></td><td>{}</td></tr>
                        <tr><td align="right"><b>Teléfono:</b></td><td>{}</td></tr>
                        <tr><td align="right"><b>Dirección:</b></td><td>{}</td></tr>
                    </table>
                </td>
                <td width="20%" align="center"></td>
                <td width="40%" align="center">
                    <h3>{}</h3>
                    <p align="center">{}</p>
                    <table>
                        <tr>
                            <th class="quote_date">Fecha</th>
                            <td>&nbsp;&nbsp;</td>
                            <th class="quote_date">Tipo</th>
                            <td>&nbsp;&nbsp;</td>
                            <th class="quote_date">Pago</th>
                        </tr>                    
                        <tr>
                            <td align="center">{}</td>
                            <td>&nbsp;&nbsp;</td>
                            <td align="center">{}</td>
                            <td>&nbsp;&nbsp;</td>
                            <td align="center">{}</td>
                        </tr>
                        <tr>
                            <th class="quote_date">Plazo</th>
                            <td>&nbsp;&nbsp;</td>
                            <td>&nbsp;&nbsp;</td>
                            <td>&nbsp;&nbsp;</td>
                            <th class="quote_date">Moneda</th>
                        </tr>                            
                            <td align="center">{}</td>
                            <td>&nbsp;&nbsp;</td>
                            <td>&nbsp;&nbsp;</td>
                            <td>&nbsp;&nbsp;</td>
                            <td align="center">{}</td>                            
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </div>
    
    """.format(filter_character(client.get("name")), client.get("id_number"), filter_character(client.get("email")),
               client.get("phone"), filter_character(
                   client.get("address")), doc_data["type"],
               doc_data["consecutive"], doc_data["date"], doc_data["payment_type"],
               doc_data["payment_method"], doc_data["pay_time"], doc_data["currency"])

    html_table_main_body = """
    <div>
        <table width="100%">
            <tr height="10%">
                <th width="10%">Cant</th>
                <th width="10%">Und</th>
                <th width="40%">Descripción</th>
                <th width="15%">Precio</th>
                <th width="10%">Desc</th>
                <th width="15%">Total</th>
            <tr>
    """
    exoneration = ""

    for line in doc_data["doc_lines"]:
        if not line["exonet"] in exoneration:
            exoneration = f"""{exoneration}<br/>{line["exonet"]}"""
        html_table_main_body = """{}
        <tr>
            <td class="table-cell" align="right">{:,.3f}</td>
            <td class="table-cell" align="center">UND</td>
            <td class="table-cell">{} {}</td>
            <td align="right" class="table-cell">{:,.3f}</td>
            <td align="right" class="table-cell">{:,.3f}</td>
            <td align="right" class="table-cell">{:,.3f}</td>
        </tr>""".format(html_table_main_body, float(line["amount"]), line["cabys"], filter_character(line["description"]),
                        float(line["price"]), float(line["discount"]),
                        (float(line["amount"]) * float(line["price"])) - float(line["discount"]))

    if float(service_total) > 0.00:
        service = """
                    <tr>
                <th align="right" class="total-header">Servicio 10%</th><td align="right" class="table-total">{:,.3f}</td>
            </tr>
        """.format(float(service_total))

    else:
        service = ""

    html_lower_body = """
            <tr>
            </tr>
            <tr>
                <td colspan=4 rowspan=6>
                    {}<br/>
                    <b>Clave:</b>
                    <br/>{}<br/><br/>
                    <b>Observaciones</b>
                    <br/>{}<br/>
                </td>
                <tr>
                    <th align="right" class="total-header">Total Gravado</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>
                <tr>
                    <th align="right" class="total-header">Total Exento</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>
                <tr>
                    <th align="right" class="total-header">Total Exonerado</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>                
                <tr>
                    <th align="right" class="total-header">SubTotal</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>
                <tr>
                    <th align="right" class="total-header">Descuento</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>
                <tr>
                    <th align="right" class="total-header">Venta Neta</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>
                {}
                <tr>
                    <th align="right" class="total-header">Impuesto</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>
                <tr>
                    <th align="right" class="total-header">Total</th>
                    <td align="right" class="table-total">{:,.3f}</td>
                </tr>             
        </table>
    </div>
    """.format(exoneration, bill_key, bill_remarks, float(gravado),
                float(exento), float(exonerado),
                float(subtotal), float(discount), 
                float(venta_neta), service,
                float(tax_total), float(main_total))

    
                                    

    html_final = """
    <footer>
    <p class="signature">
    Autorizada mediante resolución N° DGT-R-033-2019 del 20 de junio del 2019</p>
    <p align="right">
        <img src="file:///{}"  width="128" height="128" align="right">
    </p>    
    <div style="page-break-after:always;"></div>
    </footer>
    </body>
    </html>
    """.format(qr_path)

    return html_header + html_upper_body_sender + html_upper_body_doc_data + html_table_main_body + html_lower_body + html_final


def create_pdf(user_data, document, doc_flag=0):
    if doc_flag == 0:
        directory_path = "{}/{}/Tiquetes/{}/".format(base_path, user_data.get("id_number"),
                                                     document[1].strftime('%Y-%m-%d'))
    elif doc_flag == 1:
        directory_path = "{}/{}/Facturas/{}/".format(base_path, user_data.get("id_number"),
                                                     document[1].strftime('%Y-%m-%d'))
    elif doc_flag == 2:
        directory_path = "{}/{}/NC/{}/".format(base_path, user_data.get("id_number"),
                                               document[1].strftime('%Y-%m-%d'))
    else:
        directory_path = "{}/{}/ND/{}/".format(base_path, user_data.get("id_number"),
                                               document[1].strftime('%Y-%m-%d'))

    file_name = "{}.xml".format(document[0])
    print("Abriendo: ", file_name)
    if os.path.isfile('{}{}'.format(directory_path, file_name)):
        file_pointer = open("{}{}".format(
            directory_path, file_name.strip()), 'r', encoding='utf-8')
        file_data = file_pointer.read()
        dictionary_data = xmltodict.parse(file_data, encoding="utf-8")
        doc_data = {}
        if doc_flag == 0:
            dictionary_data = dictionary_data["TiqueteElectronico"]
            doc_data["type"] = "Tiquete Electrónico"
        elif doc_flag == 1:
            dictionary_data = dictionary_data["FacturaElectronica"]
            doc_data["type"] = "Factura Electrónica"
        elif doc_flag == 2:
            dictionary_data = dictionary_data["NotaCreditoElectronica"]
            doc_data["type"] = "Nota de Crédito Electrónica"
        else:
            dictionary_data = dictionary_data["NotaDebitoElectronica"]
            doc_data["type"] = "Nota de Débito Electrónica"

        doc_data["consecutive"] = dictionary_data["NumeroConsecutivo"]

        doc_data["date"] = document[1].strftime('%d-%m-%Y')
        try:
            if int(dictionary_data["CondicionVenta"]) == 1:
                doc_data["payment_type"] = "Contado"
            elif int(dictionary_data["CondicionVenta"]) == 2:
                doc_data["payment_type"] = "Crédito"
            elif int(dictionary_data["CondicionVenta"]) == 3:
                doc_data["payment_type"] = "Consignación"
            elif int(dictionary_data["CondicionVenta"]) == 4:
                doc_data["payment_type"] = "Apartado"
            elif int(dictionary_data["CondicionVenta"]) == 5:
                doc_data["payment_type"] = "Arrendamiento"
        except:
            sale_condition = int(dictionary_data["CondicionVenta"][0])

            if sale_condition == 1:
                doc_data["payment_type"] = "Contado"
            elif sale_condition == 2:
                doc_data["payment_type"] = "Crédito"
            elif sale_condition == 3:
                doc_data["payment_type"] = "Consignación"
            elif sale_condition == 4:
                doc_data["payment_type"] = "Apartado"
            elif sale_condition == 5:
                doc_data["payment_type"] = "Arrendamiento"

        if "MedioPago" in dictionary_data:
            try:
                if int(dictionary_data["MedioPago"]) == 1:
                    doc_data["payment_method"] = "Efectivo"
                if int(dictionary_data["MedioPago"]) == 2:
                    doc_data["payment_method"] = "Tarjeta"
                if int(dictionary_data["MedioPago"]) == 3:
                    doc_data["payment_method"] = "Cheque"
                if int(dictionary_data["MedioPago"]) == 4:
                    doc_data["payment_method"] = "Transferencia"
            except:
                for element in dictionary_data["MedioPago"]:
                    if int(element) == 1:
                        doc_data["payment_method"] = "Efectivo"
                    if int(element) == 2:
                        doc_data["payment_method"] = f"""{doc_data["payment_method"]} Tarjeta"""
                    if int(element) == 3:
                        doc_data["payment_method"] = f"""{doc_data["payment_method"]} Cheque"""
                    if int(element) == 4:
                        doc_data["payment_method"] = f"""{doc_data["payment_method"]} Transferencia"""

        else:
            doc_data["payment_method"] = "Efectivo"
        if "PlazoCredito" in doc_data:
            doc_data["pay_time"] = dictionary_data["PlazoCredito"]
        else:
            doc_data["pay_time"] = 0

        doc_data["currency"] = "CRC"

        doc_lines = []
        try:
            element = dictionary_data["DetalleServicio"]["LineaDetalle"]
        except:
            element = {"Detalle": "", "Cantidad": 0, "PrecioUnitario": 0,
                       "MontoTotalLinea": 0, "Impuesto": {"Codigo": 1, "Monto": 0}}

        try:
            if "Impuesto" in element:
                if "Exoneracion" in element["Impuesto"]:
                    exonet = element["Impuesto"]["Exoneracion"]
                    print(exonet)
                    exo_str = f"""Documento de exoneracion: {exonet["NumeroDocumento"]}"""
                else:
                    exo_str = ""
            else:
                exo_str = ""

            temp_dict = {"description": element["Detalle"],
                         "amount": element["Cantidad"],
                         "price": element["PrecioUnitario"],
                         "total": element["MontoTotalLinea"],
                         "exonet": exo_str,
                         "cabys": element["Codigo"]}

            if "MontoDescuento" in element:
                temp_dict["discount"] = element["MontoDescuento"]
            else:
                temp_dict["discount"] = 0

            doc_lines.append(temp_dict)
        except:

            for line in element:
                if "Impuesto" in line:
                    if "Exoneracion" in line["Impuesto"]:
                        exonet = line["Impuesto"]["Exoneracion"]
                        exo_str = f"""Documento de exoneracion: {exonet["NumeroDocumento"]}"""
                    else:
                        exo_str = ""
                else:
                    exo_str = ""
                temp_dict = {"description": line["Detalle"],
                             "amount": line["Cantidad"],
                             "price": line["PrecioUnitario"],
                             "total": line["MontoTotalLinea"],
                             "exonet": exo_str,
                             "cabys": element["Codigo"]}

                if "Descuento" in line:
                    temp_dict["discount"] = line["Descuento"]["MontoDescuento"]
                else:
                    temp_dict["discount"] = 0

                temp_dict["tax_total"] = 0
                temp_dict["service"] = 0

                doc_lines.append(temp_dict)

        doc_data["doc_lines"] = doc_lines

        client_data = dictionary_data["Receptor"]
        client = {"name": client_data["Nombre"]}

        if "Identificacion" in client_data:
            client["id_number"] = client_data["Identificacion"]["Numero"]

        else:
            client["id_number"] = ""

        if "CorreoElectronico" in client_data:
            client["email"] = client_data["CorreoElectronico"]

        else:
            client["email"] = ""

        if "Telefono" in client_data:
            client["phone"] = client_data["Telefono"]["NumTelefono"]

        else:
            client["phone"] = ""

        if "Ubicacion" in client_data:
            client["address"] = client_data["Ubicacion"]["OtrasSenas"]

        else:
            client["address"] = ""

        bill_remarks = ""
        if "InformacionReferencia" in dictionary_data:
            if int(dictionary_data["InformacionReferencia"]["Codigo"]) == 1:
                bill_remarks += "<b>Anula documento:</b>{}<br/>".format(
                    dictionary_data["InformacionReferencia"]["Numero"])
            elif int(dictionary_data["InformacionReferencia"]["Codigo"]) == 2:
                bill_remarks += "<b>Corrige monto en documento:</b>{}<br/>".format(
                    dictionary_data["InformacionReferencia"]["Numero"])
            bill_remarks += "<b>Razón:</b>{}<br/>".format(
                dictionary_data["InformacionReferencia"]["Razon"])
        if "Otros" in dictionary_data:
            bill_remarks += "<br /> " + dictionary_data["Otros"]["OtroTexto"]
        else:
            bill_remarks += ""
        if "TotalGravado" in dictionary_data["ResumenFactura"]:
            gravado = dictionary_data["ResumenFactura"]["TotalGravado"]
        else:
            gravado = 0

        if "TotalExento" in dictionary_data["ResumenFactura"]:
            exento = dictionary_data["ResumenFactura"]["TotalExento"]
        else:
            exento = 0
        
        if "TotalExonerado" in dictionary_data["ResumenFactura"]:
            exonerado = dictionary_data["ResumenFactura"]["TotalExonerado"]
        else:
            exonerado = 0

        subtotal = dictionary_data["ResumenFactura"]["TotalVenta"]

        if "TotalDescuentos" in dictionary_data["ResumenFactura"]:
            discount = dictionary_data["ResumenFactura"]["TotalDescuentos"]
        else:
            discount = 0

        venta_neta = dictionary_data["ResumenFactura"]["TotalVentaNeta"]
        service_total = dictionary_data["ResumenFactura"]["TotalOtrosCargos"]
        taxed_total = dictionary_data["ResumenFactura"]["TotalImpuesto"]
        main_total = dictionary_data["ResumenFactura"]["TotalComprobante"]

        output_data = html_creator(bill_key=dictionary_data["Clave"], user_data=user_data,
                                   doc_data=doc_data, client=client, bill_remarks=bill_remarks,
                                   subtotal=subtotal, discount=discount, main_total=main_total,
                                   tax_total=taxed_total, service_total=service_total, gravado=gravado,
                                   exento=exento, exonerado=exonerado, venta_neta=venta_neta)

        if True:

            html_file = open("""{}{}.html""".format(
                directory_path, document[0]), "w", encoding="utf-8")
            html_file.write(output_data)
            html_file.close()

            subprocess.call(["/PUNTOVENTA/Hermes/Apps/ext/wkhtmltopdf/bin/wkhtmltopdf.exe",
                             """{}{}.html""".format(
                                 directory_path, document[0]),
                             """{}{}.pdf""".format(directory_path, document[0])])

            return True

        else:
            print(document[0])
            return False

    else:
        return False


def prepare_pdf(user_data):

    user_code = user_data.get("code")

    # E Ticket
    cursor.execute("""  SELECT `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura`  FROM FACTURA_ENCABEZADO 
                        WHERE `Fenc_TiqueteElect` = '1' AND `Fenc_Pdf` < 1 AND `Par_Cod_Emp` = ? 
                        AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' 
                         AND Fenc_Fecha_Factura > #7/1/2020# """, (str(user_code),))

    tickets_to_send = cursor.fetchall()

    # E Bill
    cursor.execute("""  SELECT `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura` FROM FACTURA_ENCABEZADO 
                        WHERE `Fenc_TiqueteElect` = '2' AND `Fenc_Pdf` < 1  AND `Par_Cod_Emp` = ? 
                        AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' 
                         AND Fenc_Fecha_Factura > #7/1/2020# """, (str(user_code),))

    bills_to_send = cursor.fetchall()

    # Credit Note
    cursor.execute("""  SELECT `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` FROM Encab_NDCFact  
                        WHERE `JUS_TipoNota` = 1 AND `Fenc_Pdf` < 1 AND `Par_Cod_Emp` = ? 
                        AND NENC_FechaNota > #7/1/2020# """, (str(user_code),))

    credit_to_send = cursor.fetchall()

    # Debit Note
    cursor.execute("""  SELECT `Fenc_ConsecutivoNumerico`, `NENC_FechaNota` FROM Encab_NDCFact  
                        WHERE `JUS_TipoNota` = 2 AND `Fenc_Pdf` < 1  AND `Par_Cod_Emp` = ? 
                        AND  NENC_FechaNota > #7/1/2020# """, (str(user_code),))

    debit_to_send = cursor.fetchall()

    for ticket in tickets_to_send:
        if ticket[0]:
            if float(ticket[0]) > 0:
                if create_pdf(user_data, ticket, doc_flag=0):
                    cursor.execute(
                        """ UPDATE FACTURA_ENCABEZADO SET `Fenc_Pdf` = 1  WHERE Fenc_ConsecutivoNumerico = ? """, (str(ticket[0]),))
                    conn.commit()
                    print("Archivo {}.pdf".format(ticket[0]))
                else:
                    print("Error en tiquete: {}".format(ticket[0]))

    for bill in bills_to_send:
        if bill[0]:
            if float(bill[0]) > 0:
                if create_pdf(user_data, bill, doc_flag=1):
                    cursor.execute(
                        """ UPDATE FACTURA_ENCABEZADO SET `Fenc_Pdf` = 1 WHERE Fenc_ConsecutivoNumerico = ? """, (str(bill[0]),))
                    conn.commit()
                    print("Archivo {}.pdf".format(bill[0]))
                else:
                    print("Error en factura: {}".format(bill[0]))

    for credit in credit_to_send:
        if credit[0]:
            if float(credit[0]) > 0:
                if create_pdf(user_data, credit, doc_flag=2):
                    cursor.execute(
                        """ UPDATE Encab_NDCFact SET `Fenc_Pdf` = 1 WHERE Fenc_ConsecutivoNumerico = ? """, (str(credit[0]),))
                    conn.commit()
                    print("Archivo {}.pdf".format(credit[0]))
                else:
                    print("Error en nota de crédito: {}".format(credit[0]))

    for debit in debit_to_send:
        if debit[0]:
            if float(debit[0]) > 0:
                if create_pdf(user_data, debit, doc_flag=3):
                    cursor.execute(
                        """ UPDATE Encab_NDCFact SET `Fenc_Pdf` = 1 WHERE Fenc_ConsecutivoNumerico = ? """, (str(debit[0]),))
                    conn.commit()
                    print("Archivo {}.pdf".format(debit[0]))
                else:
                    print("Error en nota de crédito: {}".format(debit[0]))


def get_user_parameters():
    user_list = []
    query_string = """  SELECT Par_Cod_Emp, Par_Nomb_Empresa, Par_RepLegal, Par_TipoCedula, Par_Cedula,
                        Par_Telefono1, Par_Correo, PAR_Provincia, PAR_Canton, PAR_Distrito,
                        PAR_Barrio, Par_Direccion, PAR_Pin, PAR_Acceso, PAR_Contrasena, PAR_CorreoContrasena 
                        FROM PARAMETROS """
    cursor.execute(query_string)
    result = cursor.fetchall()
    for line in result:
        user_data = {"code": line[0], "store_name": line[1], "registered_name": line[2], "id_type": line[3],
                     "id_number": line[4], "phone": line[5], "email": line[6], "province": line[7],
                     "canton": line[8], "district": line[9], "street": line[10], "address": line[11], "pin": line[12],
                     "access": line[13], "password": line[14], "email_password": line[15]}
        user_list.append(user_data)
    return user_list


def get_simple_datetime():
    timezone = datetime.timezone(datetime.timedelta(hours=-6))
    current_datetime = datetime.datetime.now(timezone)
    return current_datetime.strftime('%Y-%m-%d %H:%M:%S')


def start_function():
    print("\n************\n{}\nIniciando creacion de pdfs\n".format(get_simple_datetime()))
    user_data = get_user_parameters()

    for element in user_data:
        prepare_pdf(element)


start_function()

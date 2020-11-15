from AccessConnection import AccessConnection
from Client import Client
from Article import Article
import XmlGenerator
import os
import subprocess
import time
import datetime


class ElectronicDocument:

    base_path = "/PUNTOVENTA/Hermes/Documentos"

    def __init__(self, user_code):
        self.user_code = user_code
        self.etickets = []
        self.ebills = []
        self.credit_notes = []
        self.debit_notes = []
        self.current_connection = False

    def get_doc_data(self, doc_data, user_data):

        return doc_data.get("key"), doc_data.get("consecutive"), doc_data.get("client_data"), doc_data.get("doc_date").strftime('%Y-%m-%dT%H:%M:%S-06:00'),
        doc_data.get("doc_date").strftime(
            '%Y-%m-%d'), doc_data.get("remarks"), doc_data.get("cash"), doc_data.get("card"),
        doc_data.get("check"), doc_data.get("transfer"), doc_data.get(
            "doc_type"), doc_data.get("lines"), doc_data.get("credit_time"),
        doc_data.get("service"), user_data.get("activity_code")

    def return_sender_data(self, user_data):
        return XmlGenerator.return_sender(company_name=user_data.get("registered_name"),
                                          company_id_type=user_data.get("id_type"), company_id=user_data.get("id_number"),
                                          company_title=user_data.get("store_name"), company_province=user_data.get("province"),
                                          company_canton=user_data.get("canton"), company_district=user_data.get("district"),
                                          company_street=user_data.get("street"), company_address=user_data.get("address"),
                                          company_email=user_data.get("email"), company_phone=user_data.get("phone"))

    def create_ticket_xml(self, doc_data, user_data):
        xml_result = f"{XmlGenerator.create_ticket_xml_header()}{self.populate_xml_content(doc_data, user_data, 4)}{XmlGenerator.return_ticket_close()}"

        self.write_and_sign(xml_result=xml_result, id_number=user_data.get("id_number"),
                            consecutivo=doc_data.get("consecutivo"),
                            directory_path=doc_data.get(
                                "fecha")[:doc_data.get("fecha").find("T")],
                            document_type="Tiquetes",
                            user_data=user_data)

        self.update_bill_status(1, doc_data.get("consecutivo"), 0)

    def populate_xml_content(self, doc_data, user_data, doc_type):
        xml_result = f"""
        {XmlGenerator.clave(doc_data.get("clave"))}
        {XmlGenerator.codigo_actividad(user_data.get("activity_code"))}
        {XmlGenerator.numero_consecutivo(doc_data.get("consecutivo"))}
        {XmlGenerator.fecha_emision(doc_data.get("fecha"))}
        {XmlGenerator.emisor(user_data.get("store_name"), user_data.get("id_type"), user_data.get("id_number"),
                            user_data.get("registered_name"), user_data.get("codigo_provincia"), user_data.get("codigo_canton"), 
                            user_data.get("codigo_distrito"), user_data.get("address"), user_data.get("phone"), user_data.get("email"))}"""

        if doc_type == 1:
            xml_result = f"""{xml_result}{XmlGenerator.receptor_factura(doc_data.get("cliente"))}"""

        elif doc_type == 4:
            xml_result = f"""{xml_result}{XmlGenerator.receptor_tiquete(doc_data.get("cliente"))}"""

        elif doc_type == 3:
            credit_note_data = doc_data
            doc_data = doc_data.get("datos_referencia")

            if int(doc_data.get("documento_tipo")) == 2:
                xml_result = f"""{xml_result}{XmlGenerator.receptor_factura(doc_data.get("cliente"))}"""
            else:
                xml_result = f"""{xml_result}{XmlGenerator.receptor_tiquete(doc_data.get("cliente"))}"""

        xml_result = f"""{xml_result}{XmlGenerator.condicion_venta(doc_data.get("condicion_venta"))}"""

        if int(doc_data.get("condicion_venta")) > 1:
            xml_result = f"{xml_result}{XmlGenerator.plazo_credito(int(doc_data.get('plazo_credito')))}"

        else:
            xml_result = f"""{xml_result}
            {XmlGenerator.medio_pago(int(doc_data.get("efectivo")), int(doc_data.get("tarjeta")), int(doc_data.get("cheque")), int(doc_data.get("transferencia")))}"""

        detalle_servicio = XmlGenerator.detalle_servicio(lineas=doc_data.get("lineas"),
                                                         servicio=doc_data.get(
                                                             "servicio"),
                                                         exoneracion=doc_data.get(
                                                             "exoneracion"),
                                                         tipo_exoneracion=doc_data.get(
                                                             "tipo_exoneracion"),
                                                         documento_exoneracion=doc_data.get(
                                                             "documento_exoneracion"),
                                                         institucion_exoneracion=doc_data.get(
                                                             "institucion_exoneracion"),
                                                         porcentaje_exoneracion=doc_data.get(
                                                             "porcentaje_exoneracion"),
                                                         fecha_exoneracion=doc_data.get("fecha_exoneracion"))

        xml_result = f"""{xml_result}{detalle_servicio.get("xml_data")}"""

        service_taxed_total = detalle_servicio.get("service_taxed_total")
        service_exempt_total = detalle_servicio.get("service_exempt_total")
        article_taxed = detalle_servicio.get("article_taxed")
        article_exempt = detalle_servicio.get("article_exempt")
        discount = detalle_servicio.get("discount_total")
        tax = detalle_servicio.get("tax_total")
        exonerated = detalle_servicio.get("exonerated_total")
        other_charges = detalle_servicio.get("other_charges")
        applied_article_exoneration = detalle_servicio.get(
            'applied_article_exoneration')
        applied_service_exoneration = detalle_servicio.get(
            'applied_service_exoneration')

        xml_result = '{}{}'.format(xml_result, XmlGenerator.return_bill_result(service_taxed_total=service_taxed_total,
                                                                               service_exempt_total=service_exempt_total,
                                                                               article_taxed_total=article_taxed,
                                                                               article_exempt_total=article_exempt,
                                                                               discount_total=discount, exonerated_total=exonerated, tax_total=tax,
                                                                               other_charges=other_charges, applied_article_exoneration=applied_article_exoneration,
                                                                               applied_service_exoneration=applied_service_exoneration))

        if doc_type == 3:
            xml_result = f"{xml_result}{XmlGenerator.return_doc_reference_data(reference_key=doc_data.get('clave'), reference_datetime=doc_data.get('fecha'))}"

        xml_result = '{}{}'.format(
            xml_result, XmlGenerator.return_regulation())
        if doc_data.get("observacion"):
            if len(doc_data.get("observacion")) > 0:
                xml_result = '{}{}'.format(
                    xml_result, XmlGenerator.return_remarks(doc_data.get("observacion")))

        return xml_result

    def write_and_sign(self, xml_result, id_number, consecutivo, directory_path, document_type, user_data):

        if not os.path.isdir(f"{self.base_path}"):
            os.makedirs(f"{self.base_path}")
            time.sleep(1)

        if not os.path.isdir(f"{self.base_path}/{id_number}"):
            os.makedirs(f"{self.base_path}/{id_number}")
            time.sleep(1)

        if not os.path.isdir(f"{self.base_path}/{id_number}/{document_type}"):
            os.makedirs(f"{self.base_path}/{id_number}/{document_type}")
            time.sleep(1)

        if not os.path.isdir(f"{self.base_path}/{id_number}/{document_type}/{directory_path}"):
            os.makedirs(
                f"{self.base_path}/{id_number}/{document_type}/{directory_path}")
            time.sleep(1)

        file_output = open(
            f"{self.base_path}/{id_number}/{document_type}/{directory_path}/{consecutivo}.xml", 'w', encoding='utf-8')
        file_output.write(xml_result)
        file_output.close()

        subprocess.call(["/PUNTOVENTA/Hermes/Apps/ext/PHP/php.exe", '/PUNTOVENTA/Hermes/Apps/ext/PHP/cli-signer.php',
                         '/PUNTOVENTA/Hermes/Apps/ext/{}.p12'.format(
                             user_data.get("id_number")), user_data.get("pin"),
                         f"{self.base_path}/{id_number}/{document_type}/{directory_path}/{consecutivo}.xml",
                         f"{self.base_path}/{id_number}/{document_type}/{directory_path}/{consecutivo}.xml"])

    def create_bill_xml(self, doc_data, user_data):
        xml_result = f"{XmlGenerator.create_bill_xml_header()}{self.populate_xml_content(doc_data, user_data, 1)}{XmlGenerator.return_bill_close()}"
        self.write_and_sign(xml_result=xml_result, id_number=user_data.get("id_number"),
                            consecutivo=doc_data.get("consecutivo"),
                            directory_path=doc_data.get(
                                "fecha")[:doc_data.get("fecha").find("T")],
                            document_type="Facturas",
                            user_data=user_data)
        self.update_bill_status(1, doc_data.get("consecutivo"), 0)

    def create_cn_xml(self, doc_data, user_data):
        xml_result = f"{XmlGenerator.create_credit_note_header()}{self.populate_xml_content(doc_data, user_data, 3)}{XmlGenerator.return_cn_close()}"
        self.write_and_sign(xml_result=xml_result, id_number=user_data.get("id_number"),
                            consecutivo=doc_data.get("consecutivo"),
                            directory_path=doc_data.get(
                                "fecha")[:doc_data.get("fecha").find("T")],
                            document_type="NC",
                            user_data=user_data)

        self.update_bill_status(1, doc_data.get("consecutivo"), 1)

    def create_dn_xml(self, debit, user_data):
        pass

    def prepare_docs(self, user_data):
        for ticket in self.etickets:
            if float(ticket.get("consecutivo")) > 0:
                self.create_ticket_xml(ticket, user_data)

        for bill in self.ebills:
            if float(bill.get("consecutivo")) > 0:
                self.create_bill_xml(bill, user_data)
        for credit in self.credit_notes:
            if float(credit.get("consecutivo")) > 0:
                self.create_cn_xml(credit, user_data)
        """
        for debit in self.debit_notes:
            if float(debit.get("consecutivo")) > 0:
                self.create_dn_xml(debit, user_data)                
        """

    def update_bill_status(self, status=1, doc_number="", doc_type=0):
        if doc_type:
            table = "Encab_NDCFact"
        else:
            table = "FACTURA_ENCABEZADO"

        query_string = f"""UPDATE {table} SET Fenc_EstadoProceso = ? WHERE Fenc_ConsecutivoNumerico = ? """
        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = self.current_connection.update_query(
                query_string, (str(status), doc_number,))

    def doc_reference(self, edoc_number):
        query_string = """SELECT `Fenc_Numero`, `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura`, `Fenc_Hora_Emision`, 
        `Fenc_MontoNoExonerado`, `Fenc_MontoExonerado`, `Fenc_Monto_SinImpuesto`, `Fenc_Monto_Desc`, `Fenc_Monto_IV`, `Fenc_PorServicioMesa`, `Fenc_MontoFactura`,
        `Fenc_MontoEfectivo`, `Fenc_Monto_Tarjeta`, `Fenc_MontoCheque`, `Fenc_MontoDeposito`, `Fenc_Observacion`, `Fenc_Tipo_Factura`, `Fenc_Plazo`,
        `Fenc_Exonerada`, `TipoExoneracion`, `NoDocExoneracion`, `InstExonera`, `PorcExoneracion`, `Fenc_TotalExonerado`, `FechaDocExonera`, `Fenc_Cod_Cliente`, 
        `Fenc_TiqueteElect` FROM FACTURA_ENCABEZADO WHERE  `Fenc_Numero` = ?  AND `Par_Cod_Emp` = ?"""
        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(edoc_number), self.user_code,))
            if result:
                if query_output[0][27] == 2 or '2' in query_output[0][27]:
                    reference_data = self.docs_to_sign(query_output)
                    reference_data[0]['documento_tipo'] = 2
                else:
                    reference_data = self.tickets_to_sign(query_output)
                    reference_data[0]['documento_tipo'] = 1
                
                reference_data = reference_data[0]
                return reference_data
            else:
                print(query_output)

        return {}

    def get_doc_lines(self, bill_number):
        lines = []
        query_string = """  SELECT `Art_Cod_Logico`, `DFA_Cantidad`, `DFA_PV_SinImp`, `DFA_Descuento`, `DFA_Monto_IV`, `DFA_Porc_IV`, 
        `DFA_Precio_Venta`, `DFA_Porc_Exoneracion` FROM DET_FACTURA WHERE `Fenc_Numero` = ?  """
        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(bill_number), ))
            if result:
                for counter, row in enumerate(query_output):
                    current_article = Article(row[0])
                    article_dictionary = current_article.get_article_data()
                    lines.append({'numero_linea': counter + 1, 'codigo': row[0], 'cantidad': row[1], 'detalle': article_dictionary.get("description"),
                                  'precio': row[2], 'descuento': row[3], 'impuesto': row[4], 'porcentaje_impuesto': row[5], 'total': row[6], 
                                  'porcentaje_exoneracion': row[7],
                                  'unidad': article_dictionary.get("unit"), 'codigo_impuesto': article_dictionary.get("iva_code"),
                                  'tarifa_impuesto': article_dictionary.get("iva_tarif"), 
                                  'cabys': article_dictionary.get('cabys')})

        return lines

    def doc_nc_lines(bill_number):
        lines = []
        query_string = """  SELECT `Art_Cod_Logico`, `DFA_Cantidad`, `DFA_PV_SinImp`, `DFA_Descuento`, `DFA_Monto_IV`,
        `DFA_Porc_IV`, `DFA_Precio_Venta` FROM DET_NDFact WHERE `NENC_ConsLogico` = ? """

        self.current_connection = AccessConnection()
        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(bill_number),))
            if result:
                for counter, row in enumerate(query_output):
                    current_article = Article(row[0])
                    article_dictionary = current_article.get_article_data()
                    lines.append({'numero_linea': counter + 1, 'codigo': row[0], 'cantidad': row[1],
                                  'detalle': article_dictionary.get("description"), 'precio': row[2], 'descuento': row[3],
                                  'impuesto': row[4], 'porcentaje_impuesto': row[5], 'total': row[6], })

        return lines

    def docs_to_sign(self, query_result):
        output_list = []
        for row in query_result:
            print(row)
            current_client = Client(row[26])
            output_list.append({'numero': row[0], 'clave': row[1], 'consecutivo': row[2],
                                'fecha': f"{row[3].strftime('%Y-%m-%d')}T{row[4].strftime('%H:%M:%S')}-06:00", 'gravado': row[5],
                                'exento': row[6], 'subtotal': row[7], 'descuento': row[8],
                                'impuesto': row[9], 'lineas': self.get_doc_lines(row[0]), 'servicio': row[10],
                                'total': row[11], 'efectivo': row[12], 'tarjeta': row[13],
                                'cheque': row[14], 'transferencia': row[15], 'observacion': row[16], 'condicion_venta': row[17], 'plazo_credito': row[18],
                                'exoneracion': int(row[19]) == 2, 'tipo_exoneracion': row[20], 'documento_exoneracion': row[21], 'institucion_exoneracion': row[22],
                                'porcentaje_exoneracion': row[23], 'total_exoneracion': row[24], 'fecha_exoneracion': row[25], 'cliente': current_client.get_client_data(), })

        return output_list

    def tickets_to_sign(self, query_result):
        output_list = []
        # numero, clave, consecutivo, fecha, hora,
        # gravado, exento, subtotal, descuento, impuesto,
        # servicio, total, efectivo, tarjeta, cheque,
        # transferencia, observacion
        for row in query_result:
            print(row)
            output_list.append({'numero': row[0], 'clave': row[1], 'consecutivo': row[2],
                                'fecha': f"{row[3].strftime('%Y-%m-%d')}T{row[4].strftime('%H:%M:%S')}-06:00", 'gravado': row[5],
                                'exento': row[6], 'subtotal': row[7], 'descuento': row[8],
                                'impuesto': row[9], 'lineas': self.get_doc_lines(row[0]), 'servicio': row[10],
                                'total': row[11], 'efectivo': row[12], 'tarjeta': row[13],
                                'cheque': row[14], 'transferencia': row[15], 'observacion': row[16], 'condicion_venta': row[17], 'plazo_credito': row[18],
                                'exoneracion': int(row[19]) == 2, 'tipo_exoneracion': row[20], 'documento_exoneracion': row[21], 'institucion_exoneracion': row[22],
                                'porcentaje_exoneracion': row[23], 'total_exoneracion': row[24], 'fecha_exoneracion': row[25],
                                'cliente': 'Cliente Contado', })

        return output_list

    def notes_to_sign(self, query_result):
        sign_list = []
        for row in query_result:
            if row[5] == 1:
                current_client = 'Cliente Contado'
            else:
                current_client = Client(row[5])
                current_client = current_client.get_client_data()
            sign_list.append({'clave': row[0], 'consecutivo': row[1],
                              'fecha': f"{row[2].strftime('%Y-%m-%d')}T{row[2].strftime('%H:%M:%S')}-06:00",
                              'observaciones': row[3], 'number': row[4],
                              'cliente': current_client,
                              'exempt': row[6],
                              'razon': row[8],
                              'datos_referencia': self.doc_reference(row[9])})

        return sign_list

    def get_etickets(self):
        """
            El total que devuelve access no suma el porcentaje de servicio en caso de que este se encuentre activado
        """
        query_string = """SELECT TOP 1000 `Fenc_Numero`, `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura`, `Fenc_Hora_Emision`, 
        `Fenc_MontoNoExonerado`, `Fenc_MontoExonerado`, `Fenc_Monto_SinImpuesto`, `Fenc_Monto_Desc`, `Fenc_Monto_IV`, `Fenc_PorServicioMesa`, `Fenc_MontoFactura`,
        `Fenc_MontoEfectivo`, `Fenc_Monto_Tarjeta`, `Fenc_MontoCheque`, `Fenc_MontoDeposito`, `Fenc_Observacion`, `Fenc_Tipo_Factura`, `Fenc_Plazo`,
        `Fenc_Exonerada`, `TipoExoneracion`, `NoDocExoneracion`, `InstExonera`, `PorcExoneracion`, `Fenc_TotalExonerado`, `FechaDocExonera`  
         FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '1'  AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ? 
         AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' AND Fenc_Fecha_Factura > #7/1/2020# """

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(self.user_code), ))
            if result:
                #numero, clave, consecutivo, fecha, hora, gravado, exento, subtotal, descuento, impuesto, servicio, total,
                #efectivo, tarjeta, cheque, transferencia, observacion, condicion_venta, plazo_credito
                self.etickets = self.tickets_to_sign(query_output)
            else:
                print(query_output)

    def get_ebills(self):
        query_string = """SELECT TOP 1000 `Fenc_Numero`, `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`, `Fenc_Fecha_Factura`, `Fenc_Hora_Emision`, 
        `Fenc_MontoNoExonerado`, `Fenc_MontoExonerado`, `Fenc_Monto_SinImpuesto`, `Fenc_Monto_Desc`, `Fenc_Monto_IV`, `Fenc_PorServicioMesa`, `Fenc_MontoFactura`,
        `Fenc_MontoEfectivo`, `Fenc_Monto_Tarjeta`, `Fenc_MontoCheque`, `Fenc_MontoDeposito`, `Fenc_Observacion`, `Fenc_Tipo_Factura`, `Fenc_Plazo`,
        `Fenc_Exonerada`, `TipoExoneracion`, `NoDocExoneracion`, `InstExonera`, `PorcExoneracion`, `Fenc_TotalExonerado`, `FechaDocExonera`, `Fenc_Cod_Cliente`  
         FROM FACTURA_ENCABEZADO WHERE `Fenc_TiqueteElect` = '2'  AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ?  
         AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' AND Fenc_Fecha_Factura > #7/1/2020# """

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(self.user_code), ))
            if result:
                self.ebills = self.docs_to_sign(query_output)
            else:
                print(query_output)

    def get_debit_notes(self):
        query_string = """SELECT TOP 25 `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`,  
                        `NENC_FechaNota`, `NENC_Observacion`, 
                        `NENC_Numero`, `Fenc_Cod_Cliente`, `Fenc_Exonerada`,
                        `NENC_ConsLogico`, `JUS_Clase`, `Fenc_Numero` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 2 
                        AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ? 
                        AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' AND NENC_FechaNota > #7/1/2020# """

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(self.user_code), ))
            if result:
                self.debit_notes = self.notes_to_sign(query_output)
            else:
                print(query_output)

    def get_credit_notes(self):
        query_string = """SELECT TOP 25 `Fenc_ClaveNumerica`, `Fenc_ConsecutivoNumerico`,  
                        `NENC_FechaNota`, `NENC_Observacion`, 
                        `NENC_Numero`, `Fenc_Cod_Cliente`, `Fenc_Exonerada`,
                        `NENC_ConsLogico`, `JUS_Clase`, `Fenc_Numero` FROM Encab_NDCFact WHERE `JUS_TipoNota` = 1 
                        AND `Fenc_Resultado` = 0 AND Fenc_EstadoProceso = 0 AND `Par_Cod_Emp` = ? 
                        AND `Fenc_ConsecutivoNumerico` <> '00000000000000000000' AND NENC_FechaNota > #7/1/2020# """

        self.current_connection = AccessConnection()

        if self.current_connection.status:
            query_output, result = self.current_connection.run_query(
                query_string, (str(self.user_code), ))
            if result:
                self.credit_notes = self.notes_to_sign(query_output)
            else:
                print(query_output)

from datetime import datetime
from xml.dom.minidom import Text, Element


def filter_character(string=""):
    if string:
        if "&" in string:
            string = string.replace("&", "&amp;")
        if "'" in string:
            string = string.replace("'", "&apos;")
        if "<" in string:
            string = string.replace("<", "&lt;")
        if ">" in string:
            string = string.replace(">", "&gt;")
        if '"' in string:
            string = string.replace('"', "&quot;")
    return string


def create_ticket_xml_header():
    return """<?xml version="1.0" encoding="UTF-8"?>
<TiqueteElectronico xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/tiqueteElectronico" xsi:schemaLocation="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/tiqueteElectronico">"""


def create_bill_xml_header():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <FacturaElectronica xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/facturaElectronica">
    """


def create_debit_note_header():
    return """<?xml version="1.0" encoding="utf-8"?>
    <NotaDebitoElectronica xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/notaDebitoElectronica">"""


def create_credit_note_header():
    return """<?xml version="1.0" encoding="utf-8"?>
    <NotaCreditoElectronica xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.3/notaCreditoElectronica">"""


def clave(clave_documento):
    return f"<Clave>{clave_documento}</Clave>"


def codigo_actividad(codigo):
    return f"<CodigoActividad>{codigo}</CodigoActividad>"


def numero_consecutivo(consecutivo):
    return f"<NumeroConsecutivo>{consecutivo}</NumeroConsecutivo>"


def fecha_emision(fecha):
    return f"<FechaEmision>{fecha}</FechaEmision>"


def emisor(nombre, identificacion_tipo, identificacion_numero, nombre_comercial, ubicacion_provincia, ubicacion_canton,
           ubicacion_distrito, ubicacion_otras_senas, telefono, correo_electronico):
    return f"""
            <Emisor>
                <Nombre>{filter_character(nombre)}</Nombre>            
                <Identificacion>
                    <Tipo>{identificacion_tipo}</Tipo>
                    <Numero>{identificacion_numero}</Numero>
                </Identificacion>
                <NombreComercial>{filter_character(nombre_comercial)}</NombreComercial>
                <Ubicacion>
                    <Provincia>{ubicacion_provincia}</Provincia>
                    <Canton>{ubicacion_canton}</Canton>
                    <Distrito>{ubicacion_distrito}</Distrito>
                    <OtrasSenas>{filter_character(ubicacion_otras_senas)}</OtrasSenas>
                </Ubicacion>
                <Telefono>
                    <CodigoPais>506</CodigoPais>
                    <NumTelefono>{telefono}</NumTelefono>
                </Telefono>
                <CorreoElectronico>{filter_character(correo_electronico)}</CorreoElectronico>
            </Emisor>
            """


def receptor_tiquete(nombre):
    return f"""<Receptor>
                <Nombre>{nombre}</Nombre>
            </Receptor>"""


def receptor_factura(client_data):
    nombre = filter_character(client_data.get("client_name"))
    identificacion_tipo = client_data.get("client_id_type")
    identificacion_numero = client_data.get("client_id_number")
    ubicacion_provincia = client_data.get("client_province")
    ubicacion_canton = client_data.get("client_canton")
    ubicacion_distrito = client_data.get("client_district")
    ubicacion_otras_senas = filter_character(client_data.get("client_signals"))
    telefono = client_data.get("client_phone")
    correo_electronico = filter_character(client_data.get("client_email"))

    return f"""
            <Receptor>
                <Nombre>{nombre}</Nombre>
                <Identificacion>                
                    <Tipo>{int(identificacion_tipo):02d}</Tipo>
                    <Numero>{identificacion_numero}</Numero>
                </Identificacion>
                <Ubicacion>
                    <Provincia>{ubicacion_provincia}</Provincia>
                    <Canton>{int(ubicacion_canton):02d}</Canton>
                    <Distrito>{int(ubicacion_distrito):02d}</Distrito>
                    <OtrasSenas>{ubicacion_otras_senas}</OtrasSenas>
                </Ubicacion>
                <Telefono>
                    <CodigoPais>506</CodigoPais>
                    <NumTelefono>{telefono}</NumTelefono>
                </Telefono>
                <CorreoElectronico>{correo_electronico}</CorreoElectronico>
            </Receptor>
    """


def condicion_venta(condicion):
    condicion = '{:02d}'.format(int(condicion))
    return f"<CondicionVenta>{condicion}</CondicionVenta>"


def plazo_credito(plazo=15):
    return f""" <PlazoCredito>{plazo}</PlazoCredito>
                <MedioPago>01</MedioPago>
    """


def medio_pago(efectivo, tarjeta, cheque, transferencia):
    payment_method = ""
    if efectivo > 0:
        payment_method = f"{payment_method}<MedioPago>01</MedioPago>"
    if tarjeta > 0:
        payment_method = f"{payment_method}<MedioPago>02</MedioPago>"
    if cheque > 0:
        payment_method = f"{payment_method}<MedioPago>03</MedioPago>"
    if transferencia > 0:
        payment_method = f"{payment_method}<MedioPago>04</MedioPago>"

    return payment_method


def detalle_servicio(lineas=[], servicio=0, exoneracion=0, tipo_exoneracion=1, documento_exoneracion="",
                     institucion_exoneracion="", porcentaje_exoneracion=0, fecha_exoneracion=""):

    # article_subtotal = (article_price + discount) * amount
    # article_discount = discount * amount

    discount_total = 0
    tax_total = 0
    article_taxed_total = 0
    article_exempt_total = 0
    service_taxed_total = 0
    service_exempt_total = 0
    monto_exoneracion_total = 0
    applied_service_exoneration = 0
    applied_article_exoneration = 0
    other_charges = 0
    total_lines = 0

    bill_lines = "<DetalleServicio>"

    for line in lineas:

        line_number = line.get('numero_linea')
        unit = line.get('unidad')
        iva_code = line.get('codigo_impuesto')
        iva_tarif = line.get('tarifa_impuesto')
        iva_percentage = line.get('porcentaje_impuesto')
        cabys = line.get("cabys")
        porcentaje_exoneracion = int(line.get('porcentaje_exoneracion'))
        if porcentaje_exoneracion > 0:
            if porcentaje_exoneracion > int(iva_percentage):
                porcentaje_exoneracion = int(iva_percentage)
        # else:
        #    porcentaje_exoneracion = 0
        amount = line.get('cantidad')
        if amount > 0:
            discount = int(line.get('descuento') * 1000)
            discount /= 1000

            price = round(line.get("precio"), 3) + discount

            discount *= amount
            article_subtotal = int(price * amount * 1000)
            article_subtotal /= 1000

            if line.get("servicio") is None:
                line["servicio"] = 0

            # if porcentaje_exoneracion is None:
            #    porcentaje_exoneracion = 0

            service_amount = float(servicio)

            if service_amount > 0:
                service_amount = (article_subtotal - discount) * \
                    float(servicio) / 100
                service_amount = int(service_amount * 1000)
                service_amount /= 1000

            else:
                service_amount = 0

            net_subtotal = article_subtotal - discount
            tax_amount = (net_subtotal * iva_percentage) / 100
            monto_exoneracion = (net_subtotal * porcentaje_exoneracion) / 100
            article_total = net_subtotal + tax_amount - monto_exoneracion
            other_charges += service_amount
            monto_exoneracion_total += monto_exoneracion

            if iva_percentage > 0:
                if "Sp" in unit or "St" in unit or "Spe" in unit:
                    service_taxed_total += (1 - (porcentaje_exoneracion /
                                                 iva_percentage)) * article_subtotal
                else:
                    article_taxed_total += (1 - (porcentaje_exoneracion /
                                                 iva_percentage)) * article_subtotal

            else:
                if "Sp" in unit or "St" in unit or "Spe" in unit:
                    service_taxed_total += 1 * article_subtotal
                else:
                    article_taxed_total += 1 * article_subtotal

            discount_total += discount

            description = line.get('detalle')

            name_text = Text()
            name_element = Element('Detalle')

            name_text.data = description
            name_element.appendChild(name_text)

            description = name_element.toxml()

            bill_lines = f"""{bill_lines}
                        <LineaDetalle>
                            <NumeroLinea>{line_number}</NumeroLinea>
                            <Codigo>{line.get('cabys')}</Codigo>
                            <CodigoComercial>
                                <Tipo>01</Tipo>
                                <Codigo>{line.get('codigo')}</Codigo>
                            </CodigoComercial>
                            <Cantidad>{amount:.3f}</Cantidad>
                            <UnidadMedida>{unit}</UnidadMedida>
                            {description}
                            <PrecioUnitario>{price:.5f}</PrecioUnitario>
                            <MontoTotal>{article_subtotal:.5f}</MontoTotal>"""

            total_lines = line_number + 1
            if discount > 0:
                bill_lines = f"""
                    {bill_lines}
                    <Descuento>
                        <MontoDescuento>{discount:.5f}</MontoDescuento>
                        <NaturalezaDescuento>Descuento estándar</NaturalezaDescuento>
                    </Descuento>                
                    """

            bill_lines = f"""{bill_lines}
                                <SubTotal>{net_subtotal:.5f}</SubTotal>
                                <Impuesto>
                                    <Codigo>{int(iva_code):02d}</Codigo>
                                    <CodigoTarifa>{int(iva_tarif):02d}</CodigoTarifa>
                                    <Tarifa>{iva_percentage:.2f}</Tarifa>
                                    <Monto>{tax_amount:.5f}</Monto>
                                """

            if exoneracion and iva_percentage > 0:

                if "Sp" in unit or "St" in unit or "Spe" in unit:
                    applied_service_exoneration += (article_subtotal * (
                        porcentaje_exoneracion/iva_percentage))
                else:
                    applied_article_exoneration += (article_subtotal * (
                        porcentaje_exoneracion/iva_percentage))
                bill_lines = f"""{bill_lines}
                                <Exoneracion>
                                <TipoDocumento>{int(tipo_exoneracion):02d}</TipoDocumento>
                                <NumeroDocumento>{documento_exoneracion.upper()}</NumeroDocumento>
                                <NombreInstitucion>{institucion_exoneracion.upper()}</NombreInstitucion>
                                <FechaEmision>{fecha_exoneracion.strftime('%Y-%m-%dT%H:%M:%S')}</FechaEmision>
                                <PorcentajeExoneracion>{int(porcentaje_exoneracion)}</PorcentajeExoneracion>
                                <MontoExoneracion>{monto_exoneracion:.5f}</MontoExoneracion></Exoneracion>"""

            net_tax = tax_amount - monto_exoneracion
            tax_total += net_tax

            bill_lines = f"""{bill_lines}
                            </Impuesto> 
                                <ImpuestoNeto>{(net_tax):.5f}</ImpuestoNeto>"""

            bill_lines = """{}
                <MontoTotalLinea>{:.5f}</MontoTotalLinea>
            </LineaDetalle>""".format(bill_lines, article_total)
        else:
            continue

    bill_lines = """{}</DetalleServicio>""".format(bill_lines)

    if other_charges > 0:
        bill_lines = """{}
        <OtrosCargos>
                        <TipoDocumento>06</TipoDocumento>                        
                        <Detalle>Servicio</Detalle>
                        <Porcentaje>10.00000</Porcentaje>
                        <MontoCargo>{:.5f}</MontoCargo>
        </OtrosCargos>""".format(bill_lines, other_charges)

    return{"xml_data": bill_lines, "discount_total": discount_total, "tax_total": tax_total,
           "article_taxed": article_taxed_total, "article_exempt": article_exempt_total,
           "service_taxed_total": service_taxed_total, "service_exempt_total": service_exempt_total,
           "other_charges": other_charges, "exonerated_total": monto_exoneracion_total, 'applied_article_exoneration': applied_article_exoneration,
           'applied_service_exoneration': applied_service_exoneration}


def return_bill_result(service_taxed_total, service_exempt_total,
                       article_taxed_total, article_exempt_total,
                       discount_total, tax_total, exonerated_total, other_charges,
                       applied_article_exoneration, applied_service_exoneration):
    main_subtotal = service_exempt_total + service_taxed_total + article_taxed_total + \
        article_exempt_total + applied_service_exoneration + applied_article_exoneration

    return f"""
                <ResumenFactura>    
                    <CodigoTipoMoneda>
                        <CodigoMoneda>CRC</CodigoMoneda>    
                        <TipoCambio>1.00000</TipoCambio>
                    </CodigoTipoMoneda>
                    <TotalServGravados>{service_taxed_total:.5f}</TotalServGravados>
                    <TotalServExentos>{service_exempt_total:.5f}</TotalServExentos>
                    <TotalServExonerado>{applied_service_exoneration:.5f}</TotalServExonerado>
                    <TotalMercanciasGravadas>{article_taxed_total:.5f}</TotalMercanciasGravadas>
                    <TotalMercanciasExentas>{article_exempt_total:.5f}</TotalMercanciasExentas>
                    <TotalMercExonerada>{applied_article_exoneration:.5f}</TotalMercExonerada>
                    <TotalGravado>{service_taxed_total + article_taxed_total:.5f}</TotalGravado>
                    <TotalExento>{service_exempt_total + article_exempt_total:.5f}</TotalExento>
                    <TotalExonerado>{applied_article_exoneration + applied_service_exoneration:.5f}</TotalExonerado>
                        <TotalVenta>{main_subtotal:.5f}</TotalVenta>
                        <TotalDescuentos>{discount_total:.5f}</TotalDescuentos>
                        <TotalVentaNeta>{main_subtotal - discount_total:.5f}</TotalVentaNeta>
                        <TotalImpuesto>{tax_total:.5f}</TotalImpuesto>
                        <TotalIVADevuelto>0.00000</TotalIVADevuelto>
                        <TotalOtrosCargos>{other_charges:.5f}</TotalOtrosCargos>
                        <TotalComprobante>{main_subtotal - discount_total + tax_total + other_charges:.5f}</TotalComprobante>
                </ResumenFactura>
            """


def return_doc_reference_data(reference_key="0000000000000000000000000000000000000",
                              reference_datetime="", reference_code=1, reference_reason="Anula documento"):

    doc_type = reference_key[29:31]
    if not reference_datetime:
        timezone = datetime.timezone(datetime.timedelta(hours=-6))
        current_datetime = datetime.datetime.now(timezone)
        reference_datetime = current_datetime.strftime(
            '%Y-%m-%dT%H:%M:%S-06:00')
    return """<InformacionReferencia>
                    <TipoDoc>{}</TipoDoc>
                    <Numero>{}</Numero>
                    <FechaEmision>{}</FechaEmision>
                    <Codigo>0{}</Codigo>
                    <Razon>{}</Razon>
            </InformacionReferencia>
    """.format(doc_type, reference_key,
               reference_datetime,
               reference_code,
               reference_reason)


def return_regulation():
    # return """<Normativa><NumeroResolucion>DGT-R-48-2016</NumeroResolucion>
    # <FechaResolucion>20-02-2017 13:22:22</FechaResolucion></Normativa>"""
    return ""


def return_ticket_close():
    return """</TiqueteElectronico>"""


def return_cn_close():
    return """</NotaCreditoElectronica>"""


def return_dn_close():
    return """</NotaDebitoElectronica>"""


def return_bill_close():
    return """</FacturaElectronica>"""


def return_remarks(remarks):
    name_text = Text()
    name_element = Element('OtroTexto')

    name_text.data = remarks
    name_element.appendChild(name_text)

    remarks = name_element.toxml()
    return """
    <Otros>{}</Otros>
    """.format(remarks)

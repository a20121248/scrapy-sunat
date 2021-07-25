# -*- coding: utf-8 -*-
import scrapy

class TrabajadorPeriodoItem(scrapy.Item):
    periodo = scrapy.Field()
    nro_trabajadores = scrapy.Field()
    nro_pensionistas = scrapy.Field()
    nro_prestadores_servicio = scrapy.Field()
    pass

class RepresentanteLegalItem(scrapy.Item):
    tip_doc = scrapy.Field()
    num_doc = scrapy.Field()
    nombre = scrapy.Field()
    cargo = scrapy.Field()
    fecha_desde = scrapy.Field()
    pass

class NombreItem(scrapy.Item):
    razon_social = scrapy.Field()
    fecha_baja = scrapy.Field()
    pass

class CondicionItem(scrapy.Item):
    condicion_contribuyente = scrapy.Field()
    fecha_desde = scrapy.Field()
    fecha_hasta = scrapy.Field()
    pass

class DomicilioItem(scrapy.Item):
    domicilio_fiscal = scrapy.Field()
    fecha_baja = scrapy.Field()
    pass

class SunatRepLegalItem(scrapy.Item):
    ruc = scrapy.Field()
    representantes = scrapy.Field()
    fecha_consulta = scrapy.Field()
    pass

class SunatNumtraItem(scrapy.Item):
    ruc = scrapy.Field()
    periodos = scrapy.Field()
    fecha_consulta = scrapy.Field()
    pass

class SunatInfHistItem(scrapy.Item):
    ruc = scrapy.Field()
    nombres = scrapy.Field()
    condiciones = scrapy.Field()
    domicilios = scrapy.Field()
    fecha_consulta = scrapy.Field()
    pass
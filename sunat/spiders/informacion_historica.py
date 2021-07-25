# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from sunat.items import CondicionItem, DomicilioItem, NombreItem, SunatInfHistItem
from datetime import datetime

class InformacionHistoricaSpider(scrapy.Spider):
    name = 'informacion_historica'
    YYYYMMDD_HHMMSS = datetime.now().strftime("%Y%m%d_%H%M%S")

    def __init__(self, *args, **kwargs):
        super(InformacionHistoricaSpider, self).__init__(*args, **kwargs)
        self.in_path = './1_INPUT/'
        self.out_path = './2_OUTPUT/'
        self.log_path = './3_LOG/'
        self.main_URL = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias'

        # INPUT
        dtype = {'RUC': str}
        self.input_df = pd.read_csv(self.in_path+self.filename, sep='\t', usecols=['RUC'], dtype=dtype, encoding='utf8')

        # LOG
        self.filepath_log = f"{self.log_path}{self.name}_{self.filename.split('.')[0]}_log_{self.YYYYMMDD_HHMMSS}.txt"
        with open(self.filepath_log, 'wb') as file:
            file.write('ruc\tfecha_consulta\ttipo\testado\tmensaje\n'.encode("utf8"))

    def start_requests(self):
        for row_idx, row in self.input_df.iterrows():
            ruc = row['RUC']
            data = {
                'submit': 'Información Histórica',
                'accion': 'getinfHis',
                'nroRuc': str(ruc),
                'desRuc': ''
            }
            yield scrapy.FormRequest(self.main_URL, formdata=data, meta={'cookiejar':row_idx+1,'ruc':str(ruc),'data':data}, callback=self.parse_sunat, dont_filter=True)
            
    def parse_sunat(self, response):
        ruc = response.meta.get('ruc')
        con = response.meta.get('cookiejar')
        data = response.meta.get('data')
        fecha_consulta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = ''
        msj1 = 'Ocurrio un error al momento de acceder a la información histórica para el ruc'
        msj2 = 'Surgieron problemas al procesar la consulta'
        msj3 = 'The requested URL was rejected'
        if msj1 in response.text:
            line += f'{ruc}\t{fecha_consulta}\t-\tERROR\t{msj1}\n'
        elif msj2 in response.text:
            line += f'{ruc}\t{fecha_consulta}\t-\tERROR\t{msj2}\n'
        elif msj3 in response.text:
            line += f'{ruc}\t{fecha_consulta}\t-\tERROR\t{msj3}\n'
        else:
            nombres, condiciones, domicilios = [], [], []
            tbodys = response.xpath('//table[@class="table"]/tbody')

            msj1 = ''
            for row in tbodys[0].xpath("./tr"):
                columns = row.xpath("./td/text()").extract()
                item = NombreItem()
                item['razon_social'] = columns[0].replace('\r','').replace('\n','').strip()
                item['fecha_baja'] = columns[1].replace('\r','').replace('\n','').strip()
                nombres.append(dict(item))
                if item['razon_social'] == 'No hay Información':
                    msj1 = item['razon_social']
            line += f'{ruc}\t{fecha_consulta}\t1. Nombre o Razón Social\tSUCESS\t{msj1}\n'

            msj1 = ''
            for row in tbodys[1].xpath("./tr"):
                columns = row.xpath("./td/text()").extract()
                item = CondicionItem()
                item['condicion_contribuyente'] = columns[0].replace('\r','').replace('\n','').strip()
                item['fecha_desde'] = columns[1].replace('\r','').replace('\n','').strip()
                item['fecha_hasta'] = columns[2].replace('\r','').replace('\n','').strip()
                condiciones.append(dict(item))
                if item['condicion_contribuyente'] == 'No hay Información':
                    msj1 = item['condicion_contribuyente']
            line += f'{ruc}\t{fecha_consulta}\t2. Condición del Contribuyente\tSUCESS\t{msj1}\n'

            msj1 = ''
            for row in tbodys[2].xpath("./tr"):
                columns = row.xpath("./td/text()").extract()
                item = DomicilioItem()
                item['domicilio_fiscal'] = ' '.join(columns[0].replace('\r','').replace('\n','').strip().split())
                item['fecha_baja'] = columns[1].replace('\r','').replace('\n','').strip()
                domicilios.append(dict(item))
                if item['domicilio_fiscal'] == 'No hay Información':
                    msj1 = item['domicilio_fiscal']
            line += f'{ruc}\t{fecha_consulta}\t3. Dirección del Domicilio Fiscal\tSUCESS\t{msj1}\n'

            item = SunatInfHistItem()
            item['ruc'] = ruc
            item['nombres'] = nombres
            item['condiciones'] = condiciones
            item['domicilios'] = domicilios
            item['fecha_consulta'] = fecha_consulta
            yield item

        with open(self.filepath_log, 'ab') as file:
            file.write(line.encode("utf8"))
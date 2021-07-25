# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from sunat.items import SunatNumtraItem, TrabajadorPeriodoItem
from datetime import datetime

class CantidadTrabajadoresSpider(scrapy.Spider):
    name = 'cantidad_trabajadores'
    YYYYMMDD_HHMMSS = datetime.now().strftime("%Y%m%d_%H%M%S")

    def __init__(self, *args, **kwargs):
        super(CantidadTrabajadoresSpider, self).__init__(*args, **kwargs)
        self.in_path = './1_INPUT/'
        self.out_path = './2_OUTPUT/'
        self.log_path = './3_LOG/'
        self.main_URL = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias'

        # INPUT
        dtype = {'RUC': str}
        self.input_df = pd.read_csv(self.in_path+self.filename, sep='\t', usecols=['RUC'], dtype=dtype, encoding='utf8')

        # CONTROL
        self.filepath_log = f"{self.log_path}{self.name}_{self.filename.split('.')[0]}_log_{self.YYYYMMDD_HHMMSS}.txt"
        with open(self.filepath_log, 'wb') as file:
            file.write('ruc\tfecha_consulta\testado\tmensaje\n'.encode("utf8"))

    def start_requests(self):
        for row_idx, row in self.input_df.iterrows():
            ruc = row['RUC']
            data = {
                'submit': 'Cantidad de Trabajadores y/o Prestadores de Servicio',
                'accion': 'getCantTrab',
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
        msj1 = 'Surgieron problemas al procesar la consulta'
        msj2 = 'The requested URL was rejected'
        if msj1 in response.text:
            line += f'{ruc}\t{fecha_consulta}\tERROR\t{msj1}\n'
        elif msj2 in response.text:
            line += f'{ruc}\t{fecha_consulta}\tERROR\t{msj2}\n'
        else:
            msj1 = 'No existen declaraciones presentadas por el contribuyente consultado'
            if msj1 not in response.text:
                msj1 = ''
                periodos = []
                rows = response.xpath('//table[@class="table"]/tbody/tr')            
                for row in rows:
                    columns = row.xpath("./td/text()").extract()
                    periodo_item = TrabajadorPeriodoItem()
                    periodo_item['periodo'] = columns[0].replace('-','').strip()
                    periodo_item['nro_trabajadores'] = columns[1].replace(' ','').strip().replace('NE','-9999')
                    periodo_item['nro_pensionistas'] = columns[2].replace(' ','').strip().replace('NE','-9999')
                    periodo_item['nro_prestadores_servicio'] = columns[3].replace(' ','').strip().replace('NE','-9999')
                    periodos.append(dict(periodo_item))
                
                line = f'{ruc}\t{fecha_consulta}\tSUCCESS\t{msj1}\n'                
                item = SunatNumtraItem()
                item['ruc'] = ruc
                item['periodos'] = periodos
                item['fecha_consulta'] = fecha_consulta
                yield item

        with open(self.filepath_log, 'ab') as file:
            file.write(line.encode("utf8"))
# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from sunat.items import SunatRepLegalItem, RepresentanteLegalItem
from datetime import datetime

class RepresentantesLegalesSpider(scrapy.Spider):
    name = 'representantes_legales'
    YYYYMMDD_HHMMSS = datetime.now().strftime("%Y%m%d_%H%M%S")

    def __init__(self, *args, **kwargs):
        super(RepresentantesLegalesSpider, self).__init__(*args, **kwargs)
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
                'submit': 'Representantes Legales',
                'accion': 'getRepLeg',
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
        msj1 = 'No se encontro información para representantes legales'
        msj2 = 'Surgieron problemas al procesar la consulta'
        msj3 = 'The requested URL was rejected'
        if msj1 in response.text:
            line = f'{ruc}\t{fecha_consulta}\tSUCCESS\t{msj1}\n'
        elif msj2 in response.text:
            line = f'{ruc}\t{fecha_consulta}\tERROR\t{msj2}\n'
        elif msj3 in response.text:
            line = f'{ruc}\t{fecha_consulta}\tERROR\t{msj3}\n'
        else:
            msj1 = 'No existen declaraciones presentadas por el contribuyente'
            if msj1 not in response.text:
                msj1 = ''
                representantes = []
                rows = response.xpath('//table[@class="table"]/tbody/tr')
                for row in rows:
                    columns = row.xpath("./td/text()").extract()
                    representante_item = RepresentanteLegalItem()
                    representante_item['tip_doc'] = columns[0].replace('\r','').replace('\n','').strip()
                    representante_item['num_doc'] = columns[1].replace('\r','').replace('\n','').strip()
                    representante_item['nombre'] = columns[2].replace('\r','').replace('\n','').strip()
                    representante_item['cargo'] = columns[3].replace('\r','').replace('\n','').strip()
                    representante_item['fecha_desde'] = columns[4].replace('\r','').replace('\n','').strip()
                    representantes.append(dict(representante_item))

                line = f'{ruc}\t{fecha_consulta}\tSUCCESS\t{msj1}\n'
                item = SunatRepLegalItem()
                item['ruc'] = ruc
                item['representantes'] = representantes
                item['fecha_consulta'] = fecha_consulta
                yield item

        with open(self.filepath_log, 'ab') as file:
            file.write(line.encode("utf8"))
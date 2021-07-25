# -*- coding: utf-8 -*-
import pandas as pd
from sunat.items import SunatInfHistItem, SunatNumtraItem, SunatRepLegalItem

class csvWriterPipeline(object):
    out_path = './2_OUTPUT/'
    items_written_infogeneral = 0

    def open_spider(self, spider):
        spider_name = type(spider).__name__
        if spider_name == 'CantidadTrabajadoresSpider':
            self.ctd_save_infogeneral = 1
            self.columnsPrincipal = ['ruc','periodo','nro_trabajadores','nro_pensionistas','nro_prestadores_servicio','fecha_consulta']
            self.prename_infogeneral = f"{self.out_path}{getattr(spider, 'name')}_{getattr(spider, 'filename').split('.')[0]}_{getattr(spider, 'YYYYMMDD_HHMMSS')}.txt"
        if spider_name == 'RepresentantesLegalesSpider':
            self.ctd_save_infogeneral = 1
            self.columnsPrincipal = ['ruc','tip_doc','num_doc','nombre','cargo','fecha_desde','fecha_consulta']
            self.prename_infogeneral = f"{self.out_path}{getattr(spider, 'name')}_{getattr(spider, 'filename').split('.')[0]}_{getattr(spider, 'YYYYMMDD_HHMMSS')}.txt"
        if spider_name == 'InformacionHistoricaSpider':
            self.ctd_save_infogeneral = 1
            self.columnsPrincipal = ['ruc','razon_social','fecha_baja','fecha_consulta']
            self.columnsPrincipal2 = ['ruc','condicion_contribuyente','fecha_desde','fecha_hasta','fecha_consulta']
            self.columnsPrincipal3 = ['ruc','domicilio_fiscal','fecha_baja','fecha_consulta']
            self.prename_infogeneral = f"{self.out_path}{getattr(spider, 'name')}_{getattr(spider, 'filename').split('.')[0]}_1_nombres_{getattr(spider, 'YYYYMMDD_HHMMSS')}.txt"
            self.prename_infogeneral2 = f"{self.out_path}{getattr(spider, 'name')}_{getattr(spider, 'filename').split('.')[0]}_2_condiciones_{getattr(spider, 'YYYYMMDD_HHMMSS')}.txt"
            self.prename_infogeneral3 = f"{self.out_path}{getattr(spider, 'name')}_{getattr(spider, 'filename').split('.')[0]}_3_domicilios_{getattr(spider, 'YYYYMMDD_HHMMSS')}.txt"
        self.data_encontrada_infogeneral = []
        self.data_encontrada_infogeneral2 = []
        self.data_encontrada_infogeneral3 = []

    def process_item(self, item, spider):
        item_df, item_df2, item_df3 = None, None, None
        if isinstance(item, SunatNumtraItem):
            item_df = pd.json_normalize(item['periodos'])
            item_df['ruc'] = item['ruc']
            item_df['fecha_consulta'] = item['fecha_consulta']
        if isinstance(item, SunatRepLegalItem):
            item_df = pd.json_normalize(item['representantes'])
            item_df['ruc'] = item['ruc']
            item_df['fecha_consulta'] = item['fecha_consulta']
        if isinstance(item, SunatInfHistItem):
            item_df = pd.json_normalize(item['nombres'])
            item_df['ruc'] = item['ruc']
            item_df['fecha_consulta'] = item['fecha_consulta']

            item_df2 = pd.json_normalize(item['condiciones'])
            item_df2['ruc'] = item['ruc']
            item_df2['fecha_consulta'] = item['fecha_consulta']
            self.data_encontrada_infogeneral2.append(item_df2)

            item_df3 = pd.json_normalize(item['domicilios'])
            item_df3['ruc'] = item['ruc']
            item_df3['fecha_consulta'] = item['fecha_consulta']
            self.data_encontrada_infogeneral3.append(item_df3)

        self.items_written_infogeneral += 1
        self.data_encontrada_infogeneral.append(item_df)
        if self.items_written_infogeneral % self.ctd_save_infogeneral == 0:
            self.data_encontrada_infogeneral = self.guarda_data(self.prename_infogeneral, self.columnsPrincipal, self.data_encontrada_infogeneral, self.items_written_infogeneral)
            if isinstance(item, SunatInfHistItem):
                self.data_encontrada_infogeneral2 = self.guarda_data(self.prename_infogeneral2, self.columnsPrincipal2, self.data_encontrada_infogeneral2, self.items_written_infogeneral)
                self.data_encontrada_infogeneral3 = self.guarda_data(self.prename_infogeneral3, self.columnsPrincipal3, self.data_encontrada_infogeneral3, self.items_written_infogeneral)
        return item

    def guarda_data(self, filename, columns, lista_df, ctd_items=0):
        if len(lista_df)>0:
            pd.concat(lista_df).to_csv(filename, sep='\t', header=ctd_items<=self.ctd_save_infogeneral, index=False, encoding="utf-8", columns=columns, mode='a')
        return []

    def __del__(self):
        self.guarda_data(self.prename_infogeneral, self.columnsPrincipal, self.data_encontrada_infogeneral, self.items_written_infogeneral)
        print(25*'=','THE END',25*'=')
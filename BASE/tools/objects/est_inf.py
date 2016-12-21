# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from .infr_social import inf_object
from .utils import mktable
from arcpy import DeleteField_management,FieldMappings,Merge_management,TableToTable_conversion
from arcpy.mapping import Layer, RemoveLayer, RemoveTableView, TableView
from arcpy.da import InsertCursor
from xlrd import open_workbook
from os.path import join
from os import getcwd, remove
from datetime import datetime

__all__ = ["estans_inf"]

class estans_inf(inf_object):
	def read_xlsx(self,parameters):
		book = open_workbook(parameters[0].valueAsText)
		capa = book.sheet_by_name('Capa')
		tabla = book.sheet_by_name('Tabla')
		self.rows = [tabla.row_values(i)+capa.row_values(i)[1:] if capa.row_values(i)[0] == tabla.row_values(i)[0] else tabla.row_values(i)+[1,1] for i in xrange(1,tabla.nrows)]

	def make_dbf(self):
		fields = [[u'ID_EST', u'LONG', 5, 0, 5], [u'CVE_ENT', u'TEXT', 0, 0, 2], [u'CVE_MUNC', u'TEXT', 0, 0, 5], [u'CVE_ORI', u'TEXT', 0, 0, 9], [u'CVE_LOCC', u'TEXT', 0, 0, 9], [u'NOM_ENT', u'TEXT', 0, 0, 110], [u'NOM_MUN', u'TEXT', 0, 0, 110], [u'NOM_LOC', u'TEXT', 0, 0, 110], [u'NOM_EST', u'TEXT', 0, 0, 50], [u'NOM_RESP', u'TEXT', 0, 0, 47], [u'DIR', u'TEXT', 0, 0, 89], [u'COL', u'TEXT', 0, 0, 60], [u'CP', u'TEXT', 0, 0, 5], [u'CALLE1', u'TEXT', 0, 0, 42], [u'CALLE2', u'TEXT', 0, 0, 55], [u'CALLE3', u'TEXT', 0, 0, 60], [u'CAP_EST', u'SHORT', 2, 0, 2], [u'NINOS_AP', u'SHORT', 2, 0, 2], [u'NINAS_AP', u'SHORT', 2, 0, 2], [u'NNINOS', u'SHORT', 2, 0, 2], [u'MADRES', u'SHORT', 2, 0, 2], [u'PADRES', u'SHORT', 2, 0, 2], [u'STATUS', u'TEXT', 0, 0, 12], [u'GEO', u'SHORT', 1, 0, 1], [u'LONGITUD', u'Double', 17, 14, 18], [u'LATITUD', u'Double', 17, 15, 18]]
		self.tab = mktable('n_estinfantiles.dbf',fields)
		with InsertCursor(self.tab,[fld[0] for fld in fields]) as ic:
			for row in self.rows:
				if row[1] < 10:
					row[1] = u'0'+unicode(row[1]).split('.')[0]
				ic.insertRow(row[:3]+[row[3].replace(u'250110668',u'250110060')]+[u'']+row[4:16]+[row[17],row[18],row[16]]+row[19:])
		estans_inf.mapping_file(self,self.tab)
		return self.tab

	def tab_estandar(self):
		flm = FieldMappings()
		flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;ID_EST "ID_EST" true true false 5 Long 0 5 ,First,#,{0},ID_EST,-1,-1;NOM_EST "NOM_EST" true true false 50 Text 0 0 ,First,#,{0},NOM_EST,-1,-1;NOM_RESP "NOM_RESP" true true false 47 Text 0 0 ,First,#,{0},NOM_RESP,-1,-1;DIR "DIR" true true false 89 Text 0 0 ,First,#,{0},DIR,-1,-1;COL "COL" true true false 60 Text 0 0 ,First,#,{0},COL,-1,-1;CP "CP" true true false 5 Text 0 0 ,First,#,{0},CP,-1,-1;CALLE1 "CALLE1" true true false 42 Text 0 0 ,First,#,{0},CALLE1,-1,-1;CALLE2 "CALLE2" true true false 55 Text 0 0 ,First,#,{0},CALLE2,-1,-1;CALLE3 "CALLE3" true true false 60 Text 0 0 ,First,#,{0},CALLE3,-1,-1;CAP_EST "CAP_EST" true true false 2 Short 0 2 ,First,#,{0},CAP_EST,-1,-1;NINOS_AP "NINOS_AP" true true false 2 Short 0 2 ,First,#,{0},NINOS_AP,-1,-1;NINAS_AP "NINAS_AP" true true false 2 Short 0 2 ,First,#,{0},NINAS_AP,-1,-1;NNINOS "NNINOS" true true false 2 Short 0 2 ,First,#,{0},NNINOS,-1,-1;MADRES "MADRES" true true false 2 Short 0 2 ,First,#,{0},MADRES,-1,-1;PADRES "PADRES" true true false 2 Short 0 2 ,First,#,{0},PADRES,-1,-1;STATUS "STATUS" true true false 12 Text 0 0 ,First,#,{0},STATUS,-1,-1;GEO "GEO" true true false 1 Short 0 1 ,First,#,{0},GEO,-1,-1'.format(self.tab.name))
		TableToTable_conversion(self.tab,getcwd(),u'tablaweb_{0}_estandarizada.dbf'.format(self.fch.strftime('%B%Y')),None,flm)

	def carto2010(self):
		DeleteField_management(self.lyer,[u'LATITUD','LONGITUD'])
		flm = FieldMappings()
		flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;ID_EST "ID_EST" true true false 5 Long 0 5 ,First,#,{0},ID_EST,-1,-1'.format(self.lyer.name))
		name = u'estinfantiles2010_133_{0}_{1}'.format(self.fch.strftime('%b%y'),datetime.today().strftime('%d%b%y'))
		Merge_management(self.lyer,join(u'CARTO2010',u'n_{0}.shp'.format(name)),flm)
		flm.removeAll()
		flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;ID_EST "ID_EST" true true false 5 Long 0 5 ,First,#,{0},ID_EST,-1,-1;NOM_EST "NOM_EST" true true false 50 Text 0 0 ,First,#,{0},NOM_EST,-1,-1;NOM_RESP "NOM_RESP" true true false 47 Text 0 0 ,First,#,{0},NOM_RESP,-1,-1;DIR "DIR" true true false 89 Text 0 0 ,First,#,{0},DIR,-1,-1;COL "COL" true true false 60 Text 0 0 ,First,#,{0},COL,-1,-1;CP "CP" true true false 5 Text 0 0 ,First,#,{0},CP,-1,-1;CALLE1 "CALLE1" true true false 42 Text 0 0 ,First,#,{0},CALLE1,-1,-1;CALLE2 "CALLE2" true true false 55 Text 0 0 ,First,#,{0},CALLE2,-1,-1;CALLE3 "CALLE3" true true false 60 Text 0 0 ,First,#,{0},CALLE3,-1,-1;CAP_EST "CAP_EST" true true false 2 Short 0 2 ,First,#,{0},CAP_EST,-1,-1;NINOS_AP "NINOS_AP" true true false 2 Short 0 2 ,First,#,{0},NINOS_AP,-1,-1;NINAS_AP "NINAS_AP" true true false 2 Short 0 2 ,First,#,{0},NINAS_AP,-1,-1;NNINOS "NNINOS" true true false 2 Short 0 2 ,First,#,{0},NNINOS,-1,-1;MADRES "MADRES" true true false 2 Short 0 2 ,First,#,{0},MADRES,-1,-1;PADRES "PADRES" true true false 2 Short 0 2 ,First,#,{0},PADRES,-1,-1;GEO "GEO" true true false 1 Short 0 1 ,First,#,{0},GEO,-1,-1'.format(self.tab.name))
		TableToTable_conversion(self.tab,join(getcwd(),u'CARTO2010'),u't_{0}.dbf'.format(name),None,flm)
		RemoveTableView(self.mxd.activeDataFrame,TableView(self.tab.name))
		remove('{0}.dbf'.format(self.tab.name))

	def productos_c(self):
		flm = FieldMappings()
		flm.loadFromString(u'ID_EST "ID_EST" true true false 5 Long 0 5 ,First,#,{0},ID_EST,-1,-1;CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;NOM_EST "NOM_EST" true true false 50 Text 0 0 ,First,#,{0},NOM_EST,-1,-1;NOM_RESP "NOM_RESP" true true false 47 Text 0 0 ,First,#,{0},NOM_RESP,-1,-1;DIR "DIR" true true false 89 Text 0 0 ,First,#,{0},DIR,-1,-1;COL "COL" true true false 60 Text 0 0 ,First,#,{0},COL,-1,-1;CP "CP" true true false 5 Text 0 0 ,First,#,{0},CP,-1,-1;CALLE1 "CALLE1" true true false 42 Text 0 0 ,First,#,{0},CALLE1,-1,-1;CALLE2 "CALLE2" true true false 55 Text 0 0 ,First,#,{0},CALLE2,-1,-1;CALLE3 "CALLE3" true true false 60 Text 0 0 ,First,#,{0},CALLE3,-1,-1;CAP_EST "CAP_EST" true true false 2 Short 0 2 ,First,#,{0},CAP_EST,-1,-1;NINOS_AP "NINOS_AP" true true false 2 Short 0 2 ,First,#,{0},NINOS_AP,-1,-1;NINAS_AP "NINAS_AP" true true false 2 Short 0 2 ,First,#,{0},NINAS_AP,-1,-1;NNINOS "NNINOS" true true false 2 Short 0 2 ,First,#,{0},NNINOS,-1,-1;MADRES "MADRES" true true false 2 Short 0 2 ,First,#,{0},MADRES,-1,-1;PADRES "PADRES" true true false 2 Short 0 2 ,First,#,{0},PADRES,-1,-1;STATUS "STATUS" true true false 12 Text 0 0 ,First,#,{0},STATUS,-1,-1;GEO "GEO" true true false 1 Short 0 1 ,First,#,{0},GEO,-1,-1'.format(self.lyer.name))
		Merge_management(self.lyer,join(u'PRODUCTOS_COMITE','{0}_ESTINFANTILES_{1}.shp'.format(self.fch.strftime('%Y%m'),self.fch.strftime('%m%Y'))),flm)
		lay = Layer(join(u'PRODUCTOS_COMITE','{0}_ESTINFANTILES_{1}.shp'.format(self.fch.strftime('%Y%m'),self.fch.strftime('%m%Y'))))
		estans_inf.mapping_file(self,lay)
		RemoveLayer(self.mxd.activeDataFrame,Layer(self.lyer.name))
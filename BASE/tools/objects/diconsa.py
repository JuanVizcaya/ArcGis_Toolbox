# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from .infr_social import inf_object
from .utils import mktable
from arcpy import Parameter,CalculateField_management,SelectLayerByAttribute_management,AddJoin_management,RemoveJoin_management,FieldMappings,Merge_management
from arcpy.mapping import Layer,RemoveLayer,RemoveTableView,TableView,AddTableView
from arcpy.da import InsertCursor
from xlrd import open_workbook
from os.path import join
from os import remove
from shutil import copy

__all__ = ["dicon"]

class dicon(inf_object):
	@property
	def pms_ad(self):
		pm5 = Parameter('dir_tds',u'Directorio de tiendas con coordenadas (xlsx File):'.encode("cp1254"),'Input','DEFile','Required')
		pm5.filter.list = ['xlsx','xls']
		return [pm5]

	def read_xlsx(self,parameters,messages):
		book_d = open_workbook(parameters[0].valueAsText)
		book_c = open_workbook(parameters[5].valueAsText)
		sht_d = book_d.sheet_by_index(0)
		sht_c = book_c.sheet_by_index(0)
		def fill(cve,leng):
			return unicode(int(cve)).zfill(leng)
		rd = [sht_d.row_values(i) for i in xrange(1,sht_d.nrows)]
		rows_d = [[fill(row[7],2),fill(row[7],2)+fill(row[9],3),fill(row[7],2)+fill(row[9],3)+fill(row[11],4),row[8],row[10],row[12],fill(row[0],2),row[1],fill(row[0],2)+fill(row[2],2),row[3],fill(row[0],2)+fill(row[2],2)+fill(row[4],2),row[5],fill(row[0],2)+fill(row[2],2)+fill(row[4],2)+fill(row[13],4),row[14],row[15].replace('COM','COMUNITARIO').replace('ENC','ENCARGADO').replace('PRES','PRESTADO').replace('REN','RENTADO')]+[r.replace(u'S',u'SI').replace(u'N',u'NO') if r != u'' else u'NO' for r in row[16:] if r != row[18]]+[row[18]] for row in rd]
		rows_d.sort(key=lambda row: row[12])
		rd = [sht_c.row_values(i) for i in xrange(1,sht_c.nrows)]
		rows_c = [[fill(row[0],2)+fill(row[2],2)+fill(row[4],2)+fill(row[13],4),row[0],row[2],row[4]]+row[6:13]+[row[13],fill(row[7],2),fill(row[7],2)+fill(row[9],3),(fill(row[7],2)+fill(row[9],3)+fill(row[11],4)).replace('180191741','140760140').replace('030012730','030010001').replace('040033635','040033318').replace('020020277','020021284').replace('203120023','203120001'),u'',fill(row[13],4),row[14],row[15]] for row in rd]
		#rows_c = [[fill(row[0],2)+fill(row[2],2)+fill(row[4],2)+fill(row[14],4),row[0],row[2],row[4]]+row[6:13]+[row[14],fill(row[7],2),fill(row[7],2)+fill(row[9],3),(fill(row[7],2)+fill(row[9],3)+fill(row[11],4)).replace('180191741','140760140').replace('030012730','030010001').replace('040033635','040033318').replace('020020277','020021284').replace('203120023','203120001'),u'',fill(row[14],4),row[18],row[19]] for row in rd]
		rows_c.sort(key=lambda row: row[0])
		self.rows = [d+c[1:]+[0,0,u''] for d,c in zip(rows_d,rows_c) if d[12] == c[0]]
		if len(self.rows) != sht_c.nrows-1:
			messages.AddWarning("Las claves no concordaron desde el registro no. {0}".format(len(self.rows)+1))
		copy(parameters[5].valueAsText,self.main_dir)

	def make_dbf(self):
		fields = [[u'CVE_ENT', u'TEXT', 0, 0, 2], [u'CVE_MUNC', u'TEXT', 0, 0, 5], [u'CVE_LOCC', u'TEXT', 0, 0, 9], [u'NOM_ENT', u'TEXT', 0, 0, 110], [u'NOM_MUN', u'TEXT', 0, 0, 110], [u'NOM_LOC', u'TEXT', 0, 0, 110], [u'CVE_SUC', u'TEXT', 0, 0, 2], [u'SUCURSAL', u'TEXT', 0, 0, 45], [u'CVE_UNIOPE', u'TEXT', 0, 0, 4], [u'UNIOPE', u'TEXT', 0, 0, 45], [u'CVE_ALMACE', u'TEXT', 0, 0, 6], [u'ALMACEN', u'TEXT', 0, 0, 45], [u'CVE_TD', u'TEXT', 0, 0, 10], [u'DIR', u'TEXT', 0, 0, 100], [u'TIPO_LOC', u'TEXT', 0, 0, 11], [u'ENERGIA', u'TEXT', 0, 0, 2], [u'OPC_UNICA', u'TEXT', 0, 0, 2], [u'TELEFONIA', u'TEXT', 0, 0, 2], [u'BUZ_SEP', u'TEXT', 0, 0, 2], [u'PAQMED', u'TEXT', 0, 0, 2], [u'COBELEC', u'TEXT', 0, 0, 2], [u'COBAGPOT', u'TEXT', 0, 0, 2], [u'COBTEL', u'TEXT', 0, 0, 2], [u'PRODENR', u'TEXT', 0, 0, 2], [u'LECHE', u'TEXT', 0, 0, 2], [u'PAGOPO', u'TEXT', 0, 0, 2], [u'TELECOM', u'TEXT', 0, 0, 2], [u'MOLINO', u'TEXT', 0, 0, 2], [u'TORTILLE', u'TEXT', 0, 0, 2], [u'LECHUGI', u'TEXT', 0, 0, 2], [u'AGPURIF', u'TEXT', 0, 0, 2], [u'ANUNCICO', u'TEXT', 0, 0, 2], [u'PESCA', u'TEXT', 0, 0, 2], [u'ARTDEPOR', u'TEXT', 0, 0, 2], [u'CALZADO', u'TEXT', 0, 0, 2], [u'CHEQUE', u'TEXT', 0, 0, 2], [u'CARNICER', u'TEXT', 0, 0, 2], [u'FERRETER', u'TEXT', 0, 0, 2], [u'FOTOCOPI', u'TEXT', 0, 0, 2], [u'GASLP', u'TEXT', 0, 0, 2], [u'PANADERI', u'TEXT', 0, 0, 2], [u'PAPELERI', u'TEXT', 0, 0, 2], [u'PERECEDE', u'TEXT', 0, 0, 2], [u'PRODCOMU', u'TEXT', 0, 0, 2], [u'DESPEPAL', u'TEXT', 0, 0, 2], [u'ROPA', u'TEXT', 0, 0, 2], [u'RADCIV', u'TEXT', 0, 0, 2], [u'SINERGIA', u'TEXT', 0, 0, 2], [u'LECHELIC', u'TEXT', 0, 0, 2], [u'U_SERV', u'TEXT', 0, 0, 2], [u'OTRS_TDAS', u'SHORT', 2, 0, 2], [u'CVE', u'SHORT', 2, 0, 2], [u'CVEUNIOP', u'SHORT', 1, 0, 1], [u'CVESIALM', u'SHORT', 2, 0, 2], [u'CVECOALM', u'SHORT', 4, 0, 4], [u'EDO', u'SHORT', 2, 0, 2], [u'ESTADO', u'TEXT', 0, 0, 20], [u'MPIO', u'SHORT', 3, 0, 3], [u'MUNICIPIO', u'TEXT', 0, 0, 76], [u'LOC', u'SHORT', 4, 0, 4], [u'LOCALIDAD', u'TEXT', 0, 0, 76], [u'NUMTDACT', u'SHORT', 3, 0, 3], [u'CVE_ENT1', u'TEXT', 0, 0, 2], [u'CVE_MUNC1', u'TEXT', 0, 0, 5], [u'CVE_LOCC1', u'TEXT', 0, 0, 9], [u'CVE_ACT', u'TEXT', 0, 0, 9], [u'CVE_TDACT', u'TEXT', 0, 0, 4], [u'LATITUD', u'DOUBLE', 18, 11, 19], [u'LONGITUD', u'DOUBLE', 18, 11, 19], [u'X_LAMB', u'DOUBLE', 18, 11, 19], [u'Y_LAMB', u'DOUBLE', 18, 11, 19], [u'ABRE_ENT', u'TEXT', 0, 0, 16]]
		self.tab = mktable('n_loctdico_completo.dbf',fields)
		with InsertCursor(self.tab,[fld[0] for fld in fields]) as ic:
			for row in self.rows:
				coord = dicon.chk_coor(self,[unicode(row[67]),unicode(row[68])])
				[row[67],row[68]] = [float(coord[0]),float(coord[1])]
				ic.insertRow(row)
		dicon.mapping_file(self,self.tab)
		return self.tab

	def update_dbf(self,parameters):
		cenf = Layer(parameters[3].valueAsText)
		AddJoin_management(self.tab,"CVE_ACT",cenf.name,"CVE_LOCC","KEEP_COMMON")
		expr = """def calc(fld1,fld2):
			if fld1 == 0:
				return fld2
			else:
				return fld1"""
		CalculateField_management(self.tab,"{0}.LATITUD".format(self.tab.name),"calc(!{0}.LATITUD!,!{1}.LAT_DEC!)".format(self.tab.name,cenf.name),"PYTHON",expr)
		CalculateField_management(self.tab,"{0}.LONGITUD".format(self.tab.name),"calc(!{0}.LONGITUD!,!{1}.LON_DEC!)".format(self.tab.name,cenf.name),"PYTHON",expr)
		CalculateField_management(self.tab,"{0}.ABRE_ENT".format(self.tab.name),"!{0}.ABR_ENT!".format(cenf.name),"PYTHON")
		SelectLayerByAttribute_management(self.tab,"NEW_SELECTION",""" "{0}.CVE_LOCC1" <> "{0}.CVE_ACT" """.format(self.tab.name))
		CalculateField_management(self.tab,"{0}.NOM_ENT".format(self.tab.name),"!{0}.NOM_ENT!".format(cenf.name),"PYTHON")
		CalculateField_management(self.tab,"{0}.NOM_MUN".format(self.tab.name),"!{0}.NOM_MUN!".format(cenf.name),"PYTHON")
		CalculateField_management(self.tab,"{0}.NOM_LOC".format(self.tab.name),"!{0}.NOM_LOC!".format(cenf.name),"PYTHON")
		RemoveJoin_management(self.tab)
		CalculateField_management(self.tab,"CVE_LOCC","!CVE_ACT!","PYTHON")
		CalculateField_management(self.tab,"CVE_ENT","!CVE_LOCC![:2]","PYTHON")
		CalculateField_management(self.tab,"CVE_MUNC","!CVE_LOCC![:5]","PYTHON")
		SelectLayerByAttribute_management(self.tab,"CLEAR_SELECTION")

	def shp_fin(self):
		flm = FieldMappings()
		flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;CVE_SUC "CVE_SUC" true true false 2 Text 0 0 ,First,#,{0},CVE_SUC,-1,-1;SUCURSAL "SUCURSAL" true true false 45 Text 0 0 ,First,#,{0},SUCURSAL,-1,-1;CVE_UNIOPE "CVE_UNIOPE" true true false 4 Text 0 0 ,First,#,{0},CVE_UNIOPE,-1,-1;UNIOPE "UNIOPE" true true false 45 Text 0 0 ,First,#,{0},UNIOPE,-1,-1;CVE_ALMACE "CVE_ALMACE" true true false 6 Text 0 0 ,First,#,{0},CVE_ALMACE,-1,-1;ALMACEN "ALMACEN" true true false 45 Text 0 0 ,First,#,{0},ALMACEN,-1,-1;CVE_TD "CVE_TD" true true false 10 Text 0 0 ,First,#,{0},CVE_TD,-1,-1;DIR "DIR" true true false 100 Text 0 0 ,First,#,{0},DIR,-1,-1;TIPO_LOC "TIPO_LOC" true true false 11 Text 0 0 ,First,#,{0},TIPO_LOC,-1,-1;ENERGIA "ENERGIA" true true false 2 Text 0 0 ,First,#,{0},ENERGIA,-1,-1;OPC_UNICA "OPC_UNICA" true true false 2 Text 0 0 ,First,#,{0},OPC_UNICA,-1,-1;TELEFONIA "TELEFONIA" true true false 2 Text 0 0 ,First,#,{0},TELEFONIA,-1,-1;BUZ_SEP "BUZ_SEP" true true false 2 Text 0 0 ,First,#,{0},BUZ_SEP,-1,-1;PAQMED "PAQMED" true true false 2 Text 0 0 ,First,#,{0},PAQMED,-1,-1;COBELEC "COBELEC" true true false 2 Text 0 0 ,First,#,{0},COBELEC,-1,-1;COBAGPOT "COBAGPOT" true true false 2 Text 0 0 ,First,#,{0},COBAGPOT,-1,-1;COBTEL "COBTEL" true true false 2 Text 0 0 ,First,#,{0},COBTEL,-1,-1;PRODENR "PRODENR" true true false 2 Text 0 0 ,First,#,{0},PRODENR,-1,-1;LECHE "LECHE" true true false 2 Text 0 0 ,First,#,{0},LECHE,-1,-1;PAGOPO "PAGOPO" true true false 2 Text 0 0 ,First,#,{0},PAGOPO,-1,-1;TELECOM "TELECOM" true true false 2 Text 0 0 ,First,#,{0},TELECOM,-1,-1;MOLINO "MOLINO" true true false 2 Text 0 0 ,First,#,{0},MOLINO,-1,-1;TORTILLE "TORTILLE" true true false 2 Text 0 0 ,First,#,{0},TORTILLE,-1,-1;LECHUGI "LECHUGI" true true false 2 Text 0 0 ,First,#,{0},LECHUGI,-1,-1;AGPURIF "AGPURIF" true true false 2 Text 0 0 ,First,#,{0},AGPURIF,-1,-1;ANUNCICO "ANUNCICO" true true false 2 Text 0 0 ,First,#,{0},ANUNCICO,-1,-1;PESCA "PESCA" true true false 2 Text 0 0 ,First,#,{0},PESCA,-1,-1;ARTDEPOR "ARTDEPOR" true true false 2 Text 0 0 ,First,#,{0},ARTDEPOR,-1,-1;CALZADO "CALZADO" true true false 2 Text 0 0 ,First,#,{0},CALZADO,-1,-1;CHEQUE "CHEQUE" true true false 2 Text 0 0 ,First,#,{0},CHEQUE,-1,-1;CARNICER "CARNICER" true true false 2 Text 0 0 ,First,#,{0},CARNICER,-1,-1;FERRETER "FERRETER" true true false 2 Text 0 0 ,First,#,{0},FERRETER,-1,-1;FOTOCOPI "FOTOCOPI" true true false 2 Text 0 0 ,First,#,{0},FOTOCOPI,-1,-1;GASLP "GASLP" true true false 2 Text 0 0 ,First,#,{0},GASLP,-1,-1;PANADERI "PANADERI" true true false 2 Text 0 0 ,First,#,{0},PANADERI,-1,-1;PAPELERI "PAPELERI" true true false 2 Text 0 0 ,First,#,{0},PAPELERI,-1,-1;PERECEDE "PERECEDE" true true false 2 Text 0 0 ,First,#,{0},PERECEDE,-1,-1;PRODCOMU "PRODCOMU" true true false 2 Text 0 0 ,First,#,{0},PRODCOMU,-1,-1;DESPEPAL "DESPEPAL" true true false 2 Text 0 0 ,First,#,{0},DESPEPAL,-1,-1;ROPA "ROPA" true true false 2 Text 0 0 ,First,#,{0},ROPA,-1,-1;RADCIV "RADCIV" true true false 2 Text 0 0 ,First,#,{0},RADCIV,-1,-1;SINERGIA "SINERGIA" true true false 2 Text 0 0 ,First,#,{0},SINERGIA,-1,-1;LECHELIC "LECHELIC" true true false 2 Text 0 0 ,First,#,{0},LECHELIC,-1,-1;U_SERV "U_SERV" true true false 2 Text 0 0 ,First,#,{0},U_SERV,-1,-1'.format(self.lyer.name))
		Merge_management(self.lyer,'n_loctdico_{0}_09.shp'.format(self.fch.strftime('%m%y')),flm)

	def carto2010(self):
		flm = FieldMappings()
		flm.loadFromString(u'CVE_TD "CVE_TD" true true false 10 Text 0 0 ,First,#,{0},CVE_TD,-1,-1;CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1'.format(self.lyer.name))
		Merge_management(self.lyer,join(u'CARTO2010','n_diconsat2010_133_{0}.shp'.format(self.fch.strftime('%b%y'))),flm)
		tab_f = mktable('template.dbf',[[u'OTRO', u'String', 0, 0, 2], [u'PROG_SED', u'String', 0, 0, 2], [u'CORREBAN', u'String', 0, 0, 2], [u'VENDE_TA', u'String', 0, 0, 2], [u'MOSTRADO', u'String', 0, 0, 2], [u'ESTANTER', u'String', 0, 0, 2], [u'CUEN_BAS', u'String', 0, 0, 2], [u'CUEN_REB', u'String', 0, 0, 2], [u'CUEN_REF', u'String', 0, 0, 2], [u'SENALCEL', u'String', 0, 0, 2], [u'COMPANIA', u'String', 0, 0, 8], [u'PISOFIRM', u'String', 0, 0, 2], [u'PAREDSOL', u'String', 0, 0, 2], [u'TECHOSEG', u'String', 0, 0, 2], [u'CANCELER', u'String', 0, 0, 2], [u'ILUMINAC', u'String', 0, 0, 2]])
		dicon.mapping_file(self,tab_f)
		flm.removeAll()
		flm.loadFromString(u'CVE_TD "CVE_TD" true true false 10 Text 0 0 ,First,#,{0},CVE_TD,-1,-1;CVE_SUC "CVE_SUC" true true false 2 Text 0 0 ,First,#,{0},CVE_SUC,-1,-1;SUCURSAL "SUCURSAL" true true false 45 Text 0 0 ,First,#,{0},SUCURSAL,-1,-1;CVE_UNIOPE "CVE_UNIOPE" true true false 4 Text 0 0 ,First,#,{0},CVE_UNIOPE,-1,-1;UNIOPE "UNIOPE" true true false 45 Text 0 0 ,First,#,{0},UNIOPE,-1,-1;CVE_ALMACE "CVE_ALMACE" true true false 6 Text 0 0 ,First,#,{0},CVE_ALMACE,-1,-1;ALMACEN "ALMACEN" true true false 45 Text 0 0 ,First,#,{0},ALMACEN,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;DIR "DIR" true true false 100 Text 0 0 ,First,#,{0},DIR,-1,-1;TIPO_LOC "TIPO_LOC" true true false 11 Text 0 0 ,First,#,{0},TIPO_LOC,-1,-1;ENERGIA "ENERGIA" true true false 2 Text 0 0 ,First,#,{0},ENERGIA,-1,-1;OPC_UNICA "OPC_UNICA" true true false 2 Text 0 0 ,First,#,{0},OPC_UNICA,-1,-1;TELEFONIA "TELEFONIA" true true false 2 Text 0 0 ,First,#,{0},TELEFONIA,-1,-1;BUZ_SEP "BUZ_SEP" true true false 2 Text 0 0 ,First,#,{0},BUZ_SEP,-1,-1;PAQMED "PAQMED" true true false 2 Text 0 0 ,First,#,{0},PAQMED,-1,-1;COBELEC "COBELEC" true true false 2 Text 0 0 ,First,#,{0},COBELEC,-1,-1;COBAGPOT "COBAGPOT" true true false 2 Text 0 0 ,First,#,{0},COBAGPOT,-1,-1;COBTEL "COBTEL" true true false 2 Text 0 0 ,First,#,{0},COBTEL,-1,-1;PRODENR "PRODENR" true true false 2 Text 0 0 ,First,#,{0},PRODENR,-1,-1;LECHE "LECHE" true true false 2 Text 0 0 ,First,#,{0},LECHE,-1,-1;PAGOPO "PAGOPO" true true false 2 Text 0 0 ,First,#,{0},PAGOPO,-1,-1;TELECOM "TELECOM" true true false 2 Text 0 0 ,First,#,{0},TELECOM,-1,-1;MOLINO "MOLINO" true true false 2 Text 0 0 ,First,#,{0},MOLINO,-1,-1;TORTILLE "TORTILLE" true true false 2 Text 0 0 ,First,#,{0},TORTILLE,-1,-1;LECHUGI "LECHUGI" true true false 2 Text 0 0 ,First,#,{0},LECHUGI,-1,-1;AGPURIF "AGPURIF" true true false 2 Text 0 0 ,First,#,{0},AGPURIF,-1,-1;ANUNCICO "ANUNCICO" true true false 2 Text 0 0 ,First,#,{0},ANUNCICO,-1,-1;PESCA "PESCA" true true false 2 Text 0 0 ,First,#,{0},PESCA,-1,-1;ARTDEPOR "ARTDEPOR" true true false 2 Text 0 0 ,First,#,{0},ARTDEPOR,-1,-1;CALZADO "CALZADO" true true false 2 Text 0 0 ,First,#,{0},CALZADO,-1,-1;CHEQUE "CHEQUE" true true false 2 Text 0 0 ,First,#,{0},CHEQUE,-1,-1;CARNICER "CARNICER" true true false 2 Text 0 0 ,First,#,{0},CARNICER,-1,-1;FERRETER "FERRETER" true true false 2 Text 0 0 ,First,#,{0},FERRETER,-1,-1;FOTOCOPI "FOTOCOPI" true true false 2 Text 0 0 ,First,#,{0},FOTOCOPI,-1,-1;GASLP "GASLP" true true false 2 Text 0 0 ,First,#,{0},GASLP,-1,-1;PANADERI "PANADERI" true true false 2 Text 0 0 ,First,#,{0},PANADERI,-1,-1;PAPELERI "PAPELERI" true true false 2 Text 0 0 ,First,#,{0},PAPELERI,-1,-1;PERECEDE "PERECEDE" true true false 2 Text 0 0 ,First,#,{0},PERECEDE,-1,-1;PRODCOMU "PRODCOMU" true true false 2 Text 0 0 ,First,#,{0},PRODCOMU,-1,-1;DESPEPAL "DESPEPAL" true true false 2 Text 0 0 ,First,#,{0},DESPEPAL,-1,-1;ROPA "ROPA" true true false 2 Text 0 0 ,First,#,{0},ROPA,-1,-1;RADCIV "RADCIV" true true false 2 Text 0 0 ,First,#,{0},RADCIV,-1,-1;SINERGIA "SINERGIA" true true false 2 Text 0 0 ,First,#,{0},SINERGIA,-1,-1;LECHELIC "LECHELIC" true true false 2 Text 0 0 ,First,#,{0},LECHELIC,-1,-1;OTRO "OTRO" true true false 2 Text 0 0 ,First,#,{1},OTRO,-1,-1;U_SERV "U_SERV" true true false 2 Text 0 0 ,First,#,{0},U_SERV,-1,-1;PROG_SED "PROG_SED" true true false 2 Text 0 0 ,First,#,{1},PROG_SED,-1,-1;CORREBAN "CORREBAN" true true false 2 Text 0 0 ,First,#,{1},CORREBAN,-1,-1;VENDE_TA "VENDE_TA" true true false 2 Text 0 0 ,First,#,{1},VENDE_TA,-1,-1;MOSTRADO "MOSTRADO" true true false 2 Text 0 0 ,First,#,{1},MOSTRADO,-1,-1;ESTANTER "ESTANTER" true true false 2 Text 0 0 ,First,#,{1},ESTANTER,-1,-1;CUEN_BAS "CUEN_BAS" true true false 2 Text 0 0 ,First,#,{1},CUEN_BAS,-1,-1;CUEN_REB "CUEN_REB" true true false 2 Text 0 0 ,First,#,{1},CUEN_REB,-1,-1;CUEN_REF "CUEN_REF" true true false 2 Text 0 0 ,First,#,{1},CUEN_REF,-1,-1;SENALCEL "SENALCEL" true true false 2 Text 0 0 ,First,#,{1},SENALCEL,-1,-1;COMPANIA "COMPANIA" true true false 8 Text 0 0 ,First,#,{1},COMPANIA,-1,-1;PISOFIRM "PISOFIRM" true true false 2 Text 0 0 ,First,#,{1},PISOFIRM,-1,-1;PAREDSOL "PAREDSOL" true true false 2 Text 0 0 ,First,#,{1},PAREDSOL,-1,-1;TECHOSEG "TECHOSEG" true true false 2 Text 0 0 ,First,#,{1},TECHOSEG,-1,-1;CANCELER "CANCELER" true true false 2 Text 0 0 ,First,#,{1},CANCELER,-1,-1;ILUMINAC "ILUMINAC" true true false 2 Text 0 0 ,First,#,{1},ILUMINAC,-1,-1'.format(self.tab.name,tab_f.name))
		Merge_management([self.tab,tab_f],join(u'CARTO2010',u't_diconsat2010_133_{0}.dbf'.format(self.fch.strftime('%b%y'))),flm)
		RemoveTableView(self.mxd.activeDataFrame,TableView(self.tab.name))
		RemoveTableView(self.mxd.activeDataFrame,TableView(tab_f.name))
		remove('{0}.dbf'.format(self.tab.name))
		remove('{0}.dbf'.format(tab_f.name))

	def productos_c(self):
		flm = FieldMappings()
		flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;CVE_SUC "CVE_SUC" true true false 2 Text 0 0 ,First,#,{0},CVE_SUC,-1,-1;SUCURSAL "SUCURSAL" true true false 45 Text 0 0 ,First,#,{0},SUCURSAL,-1,-1;CVE_UNIOPE "CVE_UNIOPE" true true false 4 Text 0 0 ,First,#,{0},CVE_UNIOPE,-1,-1;UNIOPE "UNIOPE" true true false 45 Text 0 0 ,First,#,{0},UNIOPE,-1,-1;CVE_ALMACE "CVE_ALMACE" true true false 6 Text 0 0 ,First,#,{0},CVE_ALMACE,-1,-1;ALMACEN "ALMACEN" true true false 45 Text 0 0 ,First,#,{0},ALMACEN,-1,-1;CVE_TD "CVE_TD" true true false 10 Text 0 0 ,First,#,{0},CVE_TD,-1,-1;DIR "DIR" true true false 100 Text 0 0 ,First,#,{0},DIR,-1,-1;TIPO_LOC "TIPO_LOC" true true false 11 Text 0 0 ,First,#,{0},TIPO_LOC,-1,-1;ENERGIA "ENERGIA" true true false 2 Text 0 0 ,First,#,{0},ENERGIA,-1,-1;OPC_UNICA "OPC_UNICA" true true false 2 Text 0 0 ,First,#,{0},OPC_UNICA,-1,-1;TELEFONIA "TELEFONIA" true true false 2 Text 0 0 ,First,#,{0},TELEFONIA,-1,-1;BUZ_SEP "BUZ_SEP" true true false 2 Text 0 0 ,First,#,{0},BUZ_SEP,-1,-1;PAQMED "PAQMED" true true false 2 Text 0 0 ,First,#,{0},PAQMED,-1,-1;COBELEC "COBELEC" true true false 2 Text 0 0 ,First,#,{0},COBELEC,-1,-1;COBAGPOT "COBAGPOT" true true false 2 Text 0 0 ,First,#,{0},COBAGPOT,-1,-1;COBTEL "COBTEL" true true false 2 Text 0 0 ,First,#,{0},COBTEL,-1,-1;PRODENR "PRODENR" true true false 2 Text 0 0 ,First,#,{0},PRODENR,-1,-1;LECHE "LECHE" true true false 2 Text 0 0 ,First,#,{0},LECHE,-1,-1;PAGOPO "PAGOPO" true true false 2 Text 0 0 ,First,#,{0},PAGOPO,-1,-1;TELECOM "TELECOM" true true false 2 Text 0 0 ,First,#,{0},TELECOM,-1,-1;MOLINO "MOLINO" true true false 2 Text 0 0 ,First,#,{0},MOLINO,-1,-1;TORTILLE "TORTILLE" true true false 2 Text 0 0 ,First,#,{0},TORTILLE,-1,-1;LECHUGI "LECHUGI" true true false 2 Text 0 0 ,First,#,{0},LECHUGI,-1,-1;AGPURIF "AGPURIF" true true false 2 Text 0 0 ,First,#,{0},AGPURIF,-1,-1;ANUNCICO "ANUNCICO" true true false 2 Text 0 0 ,First,#,{0},ANUNCICO,-1,-1;PESCA "PESCA" true true false 2 Text 0 0 ,First,#,{0},PESCA,-1,-1;ARTDEPOR "ARTDEPOR" true true false 2 Text 0 0 ,First,#,{0},ARTDEPOR,-1,-1;CALZADO "CALZADO" true true false 2 Text 0 0 ,First,#,{0},CALZADO,-1,-1;CHEQUE "CHEQUE" true true false 2 Text 0 0 ,First,#,{0},CHEQUE,-1,-1;CARNICER "CARNICER" true true false 2 Text 0 0 ,First,#,{0},CARNICER,-1,-1;FERRETER "FERRETER" true true false 2 Text 0 0 ,First,#,{0},FERRETER,-1,-1;FOTOCOPI "FOTOCOPI" true true false 2 Text 0 0 ,First,#,{0},FOTOCOPI,-1,-1;GASLP "GASLP" true true false 2 Text 0 0 ,First,#,{0},GASLP,-1,-1;PANADERI "PANADERI" true true false 2 Text 0 0 ,First,#,{0},PANADERI,-1,-1;PAPELERI "PAPELERI" true true false 2 Text 0 0 ,First,#,{0},PAPELERI,-1,-1;PERECEDE "PERECEDE" true true false 2 Text 0 0 ,First,#,{0},PERECEDE,-1,-1;PRODCOMU "PRODCOMU" true true false 2 Text 0 0 ,First,#,{0},PRODCOMU,-1,-1;DESPEPAL "DESPEPAL" true true false 2 Text 0 0 ,First,#,{0},DESPEPAL,-1,-1;ROPA "ROPA" true true false 2 Text 0 0 ,First,#,{0},ROPA,-1,-1;RADCIV "RADCIV" true true false 2 Text 0 0 ,First,#,{0},RADCIV,-1,-1;SINERGIA "SINERGIA" true true false 2 Text 0 0 ,First,#,{0},SINERGIA,-1,-1;LECHELIC "LECHELIC" true true false 2 Text 0 0 ,First,#,{0},LECHELIC,-1,-1;U_SERV "U_SERV" true true false 2 Text 0 0 ,First,#,{0},U_SERV,-1,-1'.format(self.lyer.name))
		Merge_management(self.lyer,join(u'PRODUCTOS_COMITE','{0}_TDICONSA_{1}.shp'.format(self.fch.strftime('%Y%m'),self.fch.strftime('%m%Y'))),flm)
		dicon.mapping_file(self,Layer(join(u'PRODUCTOS_COMITE','{0}_TDICONSA_{1}.shp'.format(self.fch.strftime('%Y%m'),self.fch.strftime('%m%Y')))))
		RemoveLayer(self.mxd.activeDataFrame,Layer(self.lyer.name))
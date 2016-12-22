# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function, absolute_import
from .equivalencias import calc_equiv
from arcpy import Frequency_analysis, DeleteField_management,Parameter,ListFields,env,AddField_management,SelectLayerByAttribute_management, CalculateField_management,SetProgressor,SetProgressorPosition,ResetProgressor,SetProgressorLabel
from arcpy.da import SearchCursor, UpdateCursor
from arcpy.mapping import TableView
from xlrd import open_workbook
from xlutils.copy import copy
from xlwt import easyxf
from .dbfpy.dbf import Dbf
from os import chdir, getcwd,startfile
from os.path import dirname,abspath,join
from .utils import mkd

__all__ = ["pub"]

class pub(calc_equiv):
	def __init__(self):
		calc_equiv.__init__(self)
		self.bad = easyxf('pattern: pattern solid, fore_colour yellow;')
		self.ok = easyxf('pattern: pattern solid, fore_colour green;')
		self.dbf = {} 

	@property
	def params(self):
		pm0 = Parameter('xlsx',u'Consolidado de cifras (xls file):'.encode('cp1254'),"Input","DEFile","Required")
		pm1 = Parameter('input_sht',u'Hoja(s) de datos a comprobar'.encode("cp1254"),"Input",'String','Required',multiValue=True)
		pm2 = Parameter('pres',u'Archivo(s) "vu_presxloc" para comparar cifras (dbf files):'.encode('cp1254'),"Input","GPTableView","Required",multiValue=True)
		pm3 = Parameter('input_cat',u'Catálogos disponibles'.encode("cp1254"),"Input",'String','Required')
		pm0.filter.list = ['xls']
		return [pm0,pm1,pm2,pm3]

	def updatelst(self,arch):
		book = open_workbook(arch.valueAsText)
		self.sheets = book.sheet_names()
		return [self.sheets,book]

	def set_env(self,parameters):
		cve_mun = list(set([cve[:5] for cve in self.cve_loc]))
		cve_ent = list(set([cve[:2] for cve in cve_mun]))
		self.cvs_xls = [cve_ent,cve_mun]
		self.maindir = dirname(parameters[0].valueAsText)
		mkd('AGREGADOS')
		chdir(join(self.maindir,'AGREGADOS'))
		self.book = open_workbook(parameters[0].valueAsText,formatting_info=True)
		#self.shets = [book.sheet_by_index(i) for i in xrange(book.nsheets)]
		self.wbok = copy(self.book)
		#self.wshts = [self.wbok.get_sheet(i) for i in xrange(book.nsheets)]
		env.workspace = getcwd()
		env.overwriteOutput = True

	def fld_2_dbf(self,table):
		self.tab = TableView(table.value)
		AddField_management(self.tab,*["CVE_ACT","TEXT",0,0,9])

	def dbf_treatment(self):
		SelectLayerByAttribute_management(self.tab,"NEW_SELECTION",""" "CVE_ACT" <> "CVE_LOCC" AND "CVE_ACT" <> '' AND "CVE_ACT" <> 'B' """)
		CalculateField_management(self.tab,"CVE_LOCC","!CVE_ACT!","PYTHON")
		CalculateField_management(self.tab,"CVE_MUNC","!CVE_ACT![:5]","PYTHON")
		CalculateField_management(self.tab,"CVE_ENT","!CVE_ACT![:2]","PYTHON")
		SelectLayerByAttribute_management(self.tab,"CLEAR_SELECTION")
		DeleteField_management(self.tab,"CVE_ACT")
		SelectLayerByAttribute_management(self.tab,"NEW_SELECTION",""" "CVE_LOCC" = '' AND "CVE_LOCC" = 'B' """)
		with UpdateCursor(self.tab,"CVE_MUNC") as uc:
			for row in uc:
				if not row[0] in self.cvs_xls[0]:
					uc.updateRow([''])
		SelectLayerByAttribute_management(self.tab,"NEW_SELECTION",""" "CVE_MUNC" <> '' """)
		CalculateField_management(self.tab,"CVE_ENT","!CVE_MUNC![:2]","PYTHON")
		SelectLayerByAttribute_management(self.tab,"SWITCH_SELECTION")
		with UpdateCursor(self.tab,"CVE_ENT") as uc:
			for row in uc:
				if not row[0] in self.cvs_xls[1]:
					uc.updateRow([''])
		SelectLayerByAttribute_management(self.tab,"CLEAR_SELECTION")

	"""def read_dts(self,nsht):
		self.cves = ['{0}_{1}'.format(fst,lst) for fst,lst in zip(wshts[nsht].row_values(4),wshts[nsht].row_values(5)) if lst != u'']
		self.dts = [shts[nsht].row_values(i)[1:] for i in xrange(shts[nsht].nrows-1) if shts[nsht].row_values(i)[1] in [unicode(v) for v in range(1,33)]]"""

	def make_agreg(self):
		flds = [fld.name for fld in ListFields(self.tab,None,"SmallInteger")]
		for cve in ["CVE_ENT","CVE_MUNC"]:
			Frequency_analysis(self.tab,"{0}_X_{1}.dbf".format(self.tab.name[12:19].upper(),cve[4:7]),cve,flds)
			tab_ag = TableView("{0}_X_{1}.dbf".format(self.tab.name[12:19].upper(),cve[4:7]))
			DeleteField_management(tab_ag,"FREQUENCY")
			self.dbf['{0}_{1}_{2}'.format(tab_ag.name[0],tab_ag.name[5:7],cve[4:7])] = Dbf("{0}_X_{1}.dbf".format(self.tab.name[12:19].upper(),cve[4:7]),readOnly = True)

	def sheet_comp(self,messages,sht):
		sheet = self.book.sheet_by_name(sht)
		wsht = self.wbok.get_sheet(self.book.sheet_names().index(sht))
		typ = sht[:3].upper()
		cvs_xls = {'ENT':self.cvs_xls[0],'MUN':self.cvs_xls[1]}[typ]
		fld_trgt = {'ENT':"CVE_ENT",'MUN':"CVE_MUNC"}[typ]
		strt = {'ENT':2,'MUN':4}[typ]
		ft = ['{0}_{1}|{0}_{2}_{3}'.format(sheet.row_values(5)[i],sheet.row_values(3)[i],sheet.row_values(8)[i][:2],typ).split('|') for i in xrange(sheet.ncols)]
		SetProgressor("step","Comprobando las cifras contenidas en la hoja '{0}'".format(sheet.name),0,sheet.nrows)
		for i in xrange(sheet.nrows):
			this_cve = sheet.row_values(i)[{'ENT':1,'MUN':2}[typ]]
			SetProgressorPosition(i)
			if this_cve in cvs_xls+[u'Total general']:
				SetProgressorLabel("Comprobando las cifras contenidas en la hoja '{0}'\n Clave: {1}".format(sheet.name,this_cve))
				suma = 0
				fail = 1
				for val,j in zip(sheet.row_values(i),xrange(sheet.ncols)):
					if j in range(strt,sheet.ncols-1):
						dbf = self.dbf[ft[j][1]]
						dbf_cvs = [rec[fld_trgt] for rec in dbf]
						if ft[j][0] in dbf.fieldNames:
							if this_cve == 'Total general':
								if sum([rec[ft[j][0]] for rec in dbf]) == val:
									wsht.write(i,j,val,self.ok)
									suma += val
								else:
									wsht.write(i,j,val,self.bad)
 							elif (not this_cve in dbf_cvs and val == 0) or (val == dbf[dbf_cvs.index(this_cve)][ft[j][0]]):
								wsht.write(i,j,val,self.ok)
								suma += val
							else:
								wsht.write(i,j,val,self.bad)
						else:
							fail += 1
							wsht.write(sheet.nrows+1,1,'Notas:',self.bad)
							wsht.write(sheet.nrows+fail,1,'La clave del programa {0} no se encuentra en el archivo correspondiente: {1}'.format(ft[j][0],dbf.name),self.bad)
					elif j == sheet.ncols-1:
						#messages.AddMessage('suma: {0}   valor: {1}'.format(suma,val))
						if val == suma:
							wsht.write(i,j,val,self.ok)
						else:
							wsht.write(i,j,val,self.bad)
			#elif this_cve == 'Total general':
		ResetProgressor()

	def save_book(self):
		chdir('..')
		self.wbok.save('REVISADO.xls')
		startfile('REVISADO.xls')
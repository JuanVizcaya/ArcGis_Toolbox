# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function, absolute_import
from arcpy import Exists, ListFields
from .objects.utils import map_file
from xlrd import open_workbook
from itertools import izip
from .tool import Tool

class valides(object):
	cenfe = [u'FID', u'Shape', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC', u'NOM_ENT', u'ABR_ENT', u'NOM_MUN', u'NOM_LOC', u'AMBITO', u'CVE_CARTA', u'PLANO', u'LATITUD', u'LONGITUD', u'LAT_DEC', u'LON_DEC', u'ALTITUD', u'P_TOTAL', u'P_MAS', u'P_FEM', u'V_TOT']
	regact = [u'OID', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC', u'NOM_ENT', u'NOM_ABR', u'NOM_MUN', u'NOM_LOC', u'DESCGO_ACT', u'CGO_ACT', u'AMBITO', u'FECHA_ACT']
	tabeqv = [u'OID', u'CVELOCCACT', u'CVELOCCORI', u'FECHA_ACT', u'DESCGO_ACT', u'CGO_ACT', u'NOMLOC_ACT', u'NOMLOC_ORI', u'AMBLOC_ACT', u'AMBLOC_ORI', u'NOMMUN_ACT', u'NOMMUN_ORI', u'NOMENT_ACT', u'NOMENT_ORI', u'CVEMUNCACT', u'CVEMUNCORI', u'CVEENT_ACT', u'CVEENT_ORI']
	catloc = [u'OID', u'CVE_MUNC', u'CVE_LOCC', u'NOM_LOC', u'TIPO', u'NOM_LOCORI', u'CIGEL05', u'ITER05', u'CATVIG', u'ITER10']
	locact = [u'OID', u'C_MUN', u'C_LOC', u'CVE_ENT', u'CVE_MUN', u'CVE_LOC', u'NOM_ENT', u'NOM_MUN', u'NOM_LOC', u'FCH_INI', u'P_TOTAL', u'P_MAS', u'P_FEM', u'VIV_TOTALS']
	licon = [u'FID', u'Shape', u'CVE_LECHE', u'CVE_EDO', u'CVE_MUN', u'CVE_LOC', u'NOM_EDO', u'ABRE_EDO', u'NOM_MUN', u'NOM_LOC', u'LOCURB', u'PAS', u'CALLE', u'COLONIA', u'REFNCIA', u'FAMILIAS', u'BENEFICIAR', u'NIN0A12', u'GESTLAC', u'ENFCRODIS', u'ADUL60_', u'MUJ13A15', u'MUJ45A59', u'ML_TVENTA', u'INIOPER', u'LECHE', u'NCONTR', u'CONTRATO', u'NLOCA', u'LOCAL', u'TURNO', u'TMATINI', u'TMATFIN', u'TVESINI', u'TVESFIN', u'LITROS', u'ML_TLECH', u'TIPO', u'HABITANTES', u'MUJERES', u'HOMBRES', u'AGEB', u'CPOSTAL', u'PROMOTOR', u'SUPERVISO', u'CONCESIO', u'DNRUTA', u'DSECUENCIA', u'DKMS', u'DTIEMPO', u'DSUBSIDIA', u'DFRISIA', u'DINSTITU', u'DSEMIDES', u'DFRESA', u'DVAINILLA', u'DCHOCOLATE', u'LTSBENMES']
	locsit = [u'OID', u'CVE_ITER10', u'CVECEFEMUL']
	preloc = [u'CVEENT_ORI', u'CVEMUNCORI', u'CVELOCCORI', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC']
	univer = [u'OID', u'CVE_LOCC', u'LAMBX', u'LAMBY', u'LONGI', u'LATI']
	cmuni = [u'OID', u'C_ENTIDAD', u'C_MUN', u'CVE_ENT', u'CVE_MUN', u'NOM_ENT', u'NOM_MUN', u'FCH_INICIO']
	
	def dbf(self,tab,name,fields):
	    flds_intab = [fld.name for fld in ListFields(tab.valueAsText)]
	    if fields != flds_intab and not fields in flds_intab:
	        return tab.setErrorMessage(u'El archivo {0} no tiene los campos: {1}'.format(tab.valueAsText,[fld for fld in set(fields).difference(flds_intab)]))
	    elif name is not None and name not in tab.valueAsText.split('\\')[-1]:
	        return tab.setWarningMessage(u'El archivo seleccionado contiene los campos necesarios pero el nombre no coincide, ej: {0}'.format(name))
	    else:
	        return tab

	def cvs_looks_like(self,nom,typ):
	        clase = ['CATALOGO','REGISTRO','TABLA']
	        if clase[typ] in nom.split('\\')[-1] and nom[-6:-4].isalnum():
	            return True
	        else:
	            return False

	def chk_date(self,fch):
		for elmnt,form in zip(fch.valueAsText.split('/'),[(1,32,'día'),(1,13,'mes'),(1999,2026,'año')]):
			if int(elmnt) not in range(form[0],form[1]):
				fch.setErrorMessage(u'Fecha no válida, no existe el {0} número {1}\nEl formato correcto es: dd/mm/aaaa'.format(form[2],elmnt).encode('cp1254'))
		return fch

	def chk_xls(self,arch,nsht,nrows):
		book = open_workbook(arch.valueAsText)
		if book.nsheets == nsht or nsht == None:
			if book.sheet_by_index(0).row_len(book.sheet_by_index(0).nrows-1) != nrows:
				arch.setWarningMessage(u'La hoja de datos contiene {0} campos, y deberían ser {1}'.format(book.sheet_by_index(0).row_len(book.sheet_by_index(0).nrows-1)).encode('cp1254'),nrows)
		else:
			arch.setErrorMessage(u'El archivo no contiene la cantidad correcta de hojas de datos ({0})'.format(nsht))
		return arch

class Valide_A01(Tool):
	def updateMessages(self,parameters):
		if parameters[0].altered:
		    if not Exists(parameters[0].valueAsText):
		        parameters[0].setIDMessage("Error",732,parameters[0].displayName,parameters[0].valueAsText)
		if parameters[1].altered:
		    if ListFields(parameters[0].valueAsText,parameters[1].valueAsText)[0].length != 9:
		        parameters[1].setErrorMessage("The length of {0} must be 9".format(parameters[1].valueAsText))
		if parameters[2].altered:
		    if ListFields(parameters[0].valueAsText,parameters[2].valueAsText)[0].length != 9:
		        parameters[2].setErrorMessage("The length of {0} must be 9".format(parameters[2].valueAsText))
		if parameters[1].altered and parameters[2].altered:
		    if parameters[1].valueAsText == parameters[2].valueAsText:
		        parameters[2].setErrorMessage(u"The field {0} is the same of {1}".format(parameters[2].valueAsText,parameters[1].valueAsText))
		return

	def updateParameters(self,parameters):
	    if parameters[0].value:
	        parameters[0].value = map_file(parameters[0].valueAsText)
	    if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered:
	        self.e.updateOpc()
	        parameters[3].filter.list = self.e.ms
	        parameters[3].value = self.e.ms[0]
	        self.e.updateEqv()
	        self.e.updateCat(parameters[3].value)

	    if parameters[3].altered:
	        self.e.updateCat(parameters[3].value)
	    return

class Valide_A02(Tool):
	def updateMessages(self,parameters):
		flds = ([u"CVE_LOCC"],["CVELOCCACT","CVELOCCORI","DESCGO_ACT","FECHA_ACT"])
		indx = ([9],[9,9,80,10])
		for i in xrange(2):
		    if parameters[i].altered:
		        if not Exists(parameters[i].valueAsText):
		            parameters[i].setIDMessage("Error",6)
		        else:
		            tmp = [fld for fld in flds[i] if fld not in [field.name for field in ListFields(parameters[i].valueAsText,None,"String")]]
		            if len(tmp) > 0:
		                parameters[i].setIDMessage("Error",728,", ".join(tmp))
		            else:
		                for f,j in izip(flds[i],indx[i]):
		                    if [fld for fld in ListFields(parameters[i].valueAsText) if fld.name == f][0].length != j:
		                        parameters[i].setErrorMessage("The length of {0} must be {1}".format(f,j))        
		return

	def updateParameters(self, parameters):
	    if parameters[0].value:
	        if parameters[0].valueAsText.endswith('.shp'):
	            parameters[0].value = map_file(parameters[0].valueAsText)
	    if parameters[1].value:
	        if parameters[1].valueAsText.endswith('.dbf'):
	            parameters[1].value = map_file(parameters[1].valueAsText)
	    return

class Valide_B01(Tool):
	def updateMessages(self,parameters):
		vld = valides()
		if not parameters[0].value and not parameters[2].value and not parameters[4].value:
		    parameters[0].setErrorMessage("Debes indicar al menos un catálogo".encode('cp1254'))
		for i in xrange(3):
		    if parameters[i*2].altered and not vld.cvs_looks_like(parameters[i*2].valueAsText,i):
		        parameters[i*2].setErrorMessage('El archivo no tiene el formato correcto')
		return

	def updateParameters(self,parameters):
		if parameters[0].value:
			parameters[1].enabled = True
			parameters[9].enabled = True
			parameters[7].enabled = True
			if not parameters[1].altered:
				parameters[1].value = parameters[0].valueAsText.split('\\')[-1][:-4]
			if parameters[1].value and not parameters[1].valueAsText.endswith('.dbf'):
				parameters[1].value += '.dbf'
		else:
			parameters[1].enabled = False
			parameters[9].enabled = False
			parameters[7].enabled = False

		if parameters[2].value:
			parameters[3].enabled = True
			if not parameters[3].altered:
				parameters[3].value = parameters[2].valueAsText.split('\\')[-1][:-4]
			if parameters[3].value and not parameters[3].valueAsText.endswith('.dbf'):
				parameters[3].value += '.dbf'
		else:
			parameters[3].enabled = False

		if parameters[4].value:
			parameters[5].enabled = True
			if not parameters[5].altered:
				parameters[5].value = parameters[4].valueAsText.split('\\')[-1][:-4]
			if parameters[5].value and not parameters[5].valueAsText.endswith('.dbf'):
				parameters[5].value += '.dbf'
		else:
			parameters[5].enabled = False

		if parameters[0].value and parameters[4].value:
			parameters[10].enabled = True
		else:
			parameters[10].enabled = False
		return

class Valide_B02(Tool):
	def updateParameters(self, parameters):
		for i in xrange(3):
			if parameters[i].value:
				parameters[i].value = map_file(parameters[i].valueAsText)
		return

	def updateMessages(self,parameters):
		vld = valides()
		for i,flds in zip(xrange(3),[vld.cenfe,vld.tabeqv,vld.univer]):
			if parameters[i].value:
				parameters[i] = vld.dbf(parameters[i],None,flds)
		return

class Valide_B03(Tool):
	def updateParameters(self, parameters):
		for i in xrange(2):
			if parameters[i].value:
				parameters[i].value = map_file(parameters[i].valueAsText)
		return

	def updateMessages(self,parameters):
		vld = valides()
		if parameters[0].value:
			parameters[0] = vld.dbf(parameters[0],None,vld.cenfe)
		if parameters[1].value:
			parameters[1] = vld.dbf(parameters[1],None,vld.catloc)
		return

class Valide_B04(Tool):
	def updateParameters(self,parameters):
		for i in xrange(3):
			if parameters[i].value:
				parameters[i].value = map_file(parameters[i].valueAsText)
		return

	def updateMessages(self,parameters):
		vld = valides()
		for i,flds in zip(xrange(3),[vld.cenfe,vld.tabeqv,vld.locact]):
			if parameters[i].value:
				parameters[i] = vld.dbf(parameters[i],None,flds)
		return

class Valide_C01(Tool):
	def updateParameters(self, parameters):
		if parameters[4].value:
			parameters[4].value = map_file(parameters[4].valueAsText)
		if parameters[3].value:
			parameters[3].value = parameters[3].valueAsText.split(' ')[0]
		return

	def updateMessages(self, parameters):
		vld = valides()
		if parameters[0].value:
			self.book = open_workbook(parameters[0].valueAsText)
			if self.book.sheets().__len__() != 33:
				parameters[0].setErrorMessage("El archivo no contiene los libros necesarios")
		if parameters[3].altered and len(parameters[3].valueAsText.split('/')) != 3:
			parameters[3].setErrorMessage("La fecha debe ser del formato: dd/mm/aaaa")
		if parameters[4].value:
			parameters[4] = vld.dbf(parameters[4],None,vld.cmuni)
		return

class Valide_D01(Tool):
	def updateParameters(self, parameters):
		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered and not parameters[4].altered:
			self.adm.updateOpc()
			parameters[4].filter.list = self.adm.ms
			parameters[4].value = self.adm.ms[0]
			self.adm.updateEqv()
			self.adm.updateCat(parameters[4].value)
		if parameters[4].altered:
			self.adm.updateCat(parameters[4].value)

	def updateMessages(self,parameters):
		vld = valides()
		if parameters[2].value:
			parameters[2] = vld.dbf(parameters[2],'locsiter10vscenfemul',vld.locsit)
		if parameters[3].value:
			parameters[3] = vld.dbf(parameters[3],None,vld.cmuni)
		return

class Valide_D02(Tool):
	def updateParameters(self, parameters):
		for i in xrange(6):
			if parameters[i].value:
				parameters[i].value = map_file(parameters[i].valueAsText)
		return

	def updateMessages(self, parameters):
		vld = valides()
		if not parameters[0].value and not parameters[1].value and not parameters[2].value and not parameters[3].value and not parameters[4].value and not parameters[5].value:
			parameters[0].setErrorMessage("Debes indicar al menos una tabla para procesar")
		flds_lst = [[u'OID', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC', u'NOM_ENT', u'ABR_ENT', u'NOM_MUN', u'NOM_LOC', u'AMBITO', u'CVE_CARTA', u'PLANO', u'LATITUD', u'LONGITUD', u'LAT_DEC', u'LON_DEC', u'ALTITUD', u'P_TOTAL', u'P_MAS', u'P_FEM', u'V_TOT'], [u'OID', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC', u'CVE_AGEBC', u'NOM_ENT', u'NOM_MUN', u'NOM_LOC'], [u'OID', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC', u'CVE_AGEBC', u'CVE_MZAC', u'NOM_ENT', u'NOM_MUN', u'NOM_LOC'], [u'OID', u'C_codigo_p', u'Cve_codigo', u'Nom_codigo', u'C_municipi', u'Fch_inicio', u'Cve_munici'], [u'OID', u'C_asentami', u'Cve_asenta', u'Nom_asenta', u'C_codigo_p', u'Fch_inicio'], [u'OID', u'C_VIALIDAD', u'NOM_VIAL', u'ENTIDAD_ID', u'MUN_ID', u'ID_LOC', u'CVE_LOCC', u'CVE_ACT', u'CVE_MUNC']]
		for i,flds in zip(xrange(6),flds_lst):
			if parameters[i].value:
				parameters[i] = vld.dbf(parameters[i],None,flds)
		return

class Valide_D03(Tool):
	def updateParameters(self, parameters):
		for i in xrange(6):
			if parameters[i].value:
				parameters[i].value = map_file(parameters[i].valueAsText)
			if parameters[7].value:
				parameters[7].value = parameters[7].valueAsText.split(' ')[0]
		return

	def updateMessages(self,parameters):
		vld = valides()
		flds_lst = [[u'OID', u'C_AGEB', u'CVE_AGEB', u'C_LOCALI', u'FCH_INICIO', u'FCH_FINAL'], [u'OID', u'CVE_ITER10', u'CVECEFEMUL'], [u'OID', u'CVE_ENT', u'CVE_MUNC', u'CVE_LOCC', u'NOM_ENT', u'ABR_ENT', u'NOM_MUN', u'NOM_LOC', u'AMBITO', u'CVE_CARTA', u'PLANO', u'LATITUD', u'LONGITUD', u'LAT_DEC', u'LON_DEC', u'ALTITUD', u'P_TOTAL', u'P_MAS', u'P_FEM', u'V_TOT', u'ID_LOC', u'ENTIDAD_ID', u'MUN_ID', u'CVE_LOCNUM', u'CVE_LOCSTR', u'ESTRATO', u'IRS', u'AGEB_URB', u'SITUA_LOC'], [u'OID', u'ID_LOC', u'AGEB', u'AGEB_ID', u'MUN_ID', u'ENTIDAD_ID'], [u'OID', u'C_MANZANA', u'CVE_MANZAN', u'C_AGEB', u'FCH_INICIO', u'FCH_FINAL'], [u'OID', u'AGEB_ID', u'CVE_MZAC', u'MANZANA_ID', u'ENTIDAD_ID', u'MANZANA', u'MUN_ID', u'CVE_LOCNUM', u'CVE_LOCC', u'AGEB']]
		for i,flds in zip(xrange(6),flds_lst):
			if parameters[i].value:
				parameters[i] = vld.dbf(parameters[i],None,flds)
		return

class Valide_E01(Tool):
	def updateParameters(self,parameters):
		for i in [0,3]:
			if parameters[i].value:
				parameters[i].value = map_file(parameters[i].valueAsText)
		if parameters[1].value:
			parameters[1].value = parameters[1].valueAsText.split(' ')[0]
		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered and not parameters[4].altered:
			self.l.updateOpc()
			parameters[4].filter.list = self.l.ms
			parameters[4].value = self.l.ms[0]
			self.l.updateEqv()
			self.l.updateCat(parameters[4].value)
		if parameters[4].altered:
			self.l.updateCat(parameters[4].value)
		return

	def updateMessages(self,parameters):
		vld = valides()
		if parameters[0].value:
			parameters[0] = vld.dbf(parameters[0],None,vld.licon)
		if parameters[1].value:
			parameters[1] = vld.chk_date(parameters[1])
		if parameters[3].value:
			parameters[3] = vld.dbf(parameters[3],None,vld.cenfe)
		return

class Valide_E02(Tool):
	def updateParameters(self,parameters):
		if parameters[3].value:
			parameters[3].value = map_file(parameters[3].valueAsText)
		if parameters[1].value:
			parameters[1].value = parameters[1].valueAsText.split(' ')[0]
		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered and not parameters[4].altered and not parameters[5].altered:
			self.d.updateOpc()
			parameters[4].filter.list = self.d.ms
			parameters[4].value = self.d.ms[0]
			self.d.updateEqv()
			self.d.updateCat(parameters[4].value)
		if parameters[4].altered:
			self.d.updateCat(parameters[4].value)
		return

	def updateMessages(self,parameters):
		vld = valides()
		for i,n in zip([0,5],[52,16]):
			if parameters[i].value:
				parameters[i] = vld.chk_xls(parameters[i],1,n)
		if parameters[1].value:
			parameters[1] = vld.chk_date(parameters[1])
		if parameters[3].value:
			parameters[3] = vld.dbf(parameters[3],None,vld.cenfe)
		return

class Valide_E03(Tool):
	def updateParameters(self,parameters):
		if parameters[3].value:
			parameters[3].value = map_file(parameters[3].valueAsText)

		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered and not parameters[4].altered:
			self.ei.updateOpc()
			parameters[4].filter.list = self.ei.ms
			parameters[4].value = self.ei.ms[0]
			self.ei.updateEqv()
			self.ei.updateCat(parameters[4].value)
		if parameters[4].altered:
			self.ei.updateCat(parameters[4].value)
		return

	def updateMessages(self,parameters):
		vld = valides()
		if parameters[0].value:
			parameters[0] = vld.chk_xls(parameters[0],2,3)
		if parameters[1].value:
			parameters[1] = vld.chk_date(parameters[1])
		if parameters[3].value:
			parameters[3] = vld.dbf(parameters[3],None,vld.cenfe)
		return

class Valide_E04(Tool):
	def updateParameters(self,parameters):
		if parameters[3].value:
			parameters[3].value = map_file(parameters[3].valueAsText)

		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered and not parameters[4].altered:
			self.cc.updateOpc()
			parameters[4].filter.list = self.cc.ms
			parameters[4].value = self.cc.ms[0]
			self.cc.updateEqv()
			self.cc.updateCat(parameters[4].value)
		if parameters[4].altered:
			self.cc.updateCat(parameters[4].value)
		return

	def updateMessages(self,parameters):
		return

class Valide_F01(Tool):
	def updateParameters(self,parameters):
		if parameters[2].value:
			parameters[2].values = [map_file(pm.value) for pm in parameters[2].values]
			#for pm in parameters[1].values:
				#pm = map_file(pm.value)
		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered:
			self.p.updateOpc()
			parameters[3].filter.list = self.p.ms
			parameters[3].value = self.p.ms[0]
			self.p.updateEqv()
			self.p.updateCat(parameters[3].value)
		if parameters[3].altered:
			self.p.updateCat(parameters[3].value)
		if parameters[0].altered:
			parameters[1].filter.list = self.p.updatelst(parameters[0])[0]

	def updateMessages(self,parameters):
		vld = valides()
		if parameters[0].value:
			shtlst = self.p.updatelst(parameters[0])[0]
			for sht in shtlst:
				if 'Municipio' in sht or 'Entidad' in sht:
					break
				elif sht == shtlst[-1]:
					parameters[0].setWarningMessage('El archivo no contiene hojas de datos con el nombre convencional')
		if parameters[1].value:
			for sht in parameters[1].values:
				sheet = self.p.updatelst(parameters[0])[1].sheet_by_name(sht)
				if not sheet.cell_value(8,1) in ['CVEEDO','CVEENT','CVE_ENT'] or sheet.cell_value(sheet.nrows-1,1) != 'Total general':
					parameters[1].setErrorMessage('La hoja de datos "{0}" no cumple con las características adecuadas'.format(sht).encode('cp1254'))
		if parameters[2].value:
			for dbf in parameters[2].values:
				if not 'vu_presxloc' in dbf.value:
					parameters[2].setErrorMessage('El archivo {0} no tiene el nombre correcto, favor de verificarlo.'.format(dbf))
				elif set(vld.preloc).intersection([fld.name for fld in ListFields(dbf.value)]) != set(vld.preloc):
					parameters[2].setErrorMessage('El archivo {0} no contiene los campos correctos, favor de verificarlo.'.format(dbf))

class Valide_F02(Tool):
	def updateParameters(self, parameters):
		if parameters[0].value:
			parameters[0].value = map_file(parameters[0].valueAsText)
		if not parameters[0].altered and not parameters[1].altered and not parameters[2].altered and not parameters[3].altered and not parameters[4].altered:
			self.PS.updateOpc()
			parameters[4].filter.list = self.PS.ms
			parameters[4].value = self.PS.ms[0]
			self.PS.updateEqv()
			self.PS.updateCat(parameters[4].value)
            
		if parameters[4].altered:
			self.PS.updateCat(parameters[4].value)

		if parameters[3].altered:
			self.PS.check_extension(parameters[3])
		return

	def updateMessages(self,parameters):
		if parameters[1].altered:
			if not Exists(parameters[1].valueAsText):
				parameters[1].setIDMessage("Error",732,parameters[1].displayName,parameters[1].valueAsText)
		return
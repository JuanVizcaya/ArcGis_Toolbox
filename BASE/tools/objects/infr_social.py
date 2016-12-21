# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from .utils import mkd, mklistdir
from arcpy import env,SpatialReference, Parameter, RefreshTOC, RefreshActiveView, MakeXYEventLayer_management, Project_management, CalculateField_management,AddJoin_management,SelectLayerByAttribute_management,RemoveJoin_management,DeleteField_management
from arcpy.mapping import AddTableView,MapDocument,AddLayer,Layer,RemoveLayer,ListLayers
from arcpy.da import  SearchCursor
from os import getcwd, chdir, remove, walk
from os.path import join, dirname, abspath
from shutil import copy
from datetime import datetime
from .equivalencias import calc_equiv
from .data import bar

__all__ = ["inf_object"]

class inf_object(calc_equiv):
	def __init__(self):
		self.__licens = "users"
		self.path = bar.fpath
		self.root = dirname(abspath(__file__))
		self.mxd = MapDocument("CURRENT")

	@property
	def _license(self):
		return True
		#return utils.license_v2(utils.licens.lists[self.__licens])

	@property
	def barrendero(self):
		chdir(self.main_dir)
		for root, dirs, files in walk(".", topdown=False):
			for name in files:
				if name.endswith('.xml') or name.endswith('.sbn') or name.endswith('.sbx'):
					remove(join(root, name))

	def params(self,process):
		pm0 = Parameter('br_cc',u'{0} (xlsx File):'.format(process).encode("cp1254"),'Input','DEFile','Required')
		pm1 = Parameter('fch_act',u'Fecha de actualización (dd/mm/aaaa):'.encode('cp1254'),'Input','GPDate','Required')
		pm2 = Parameter('savedir',u'Ruta de salida:','Input','DEWorkspace','Required')
		pm3 = Parameter('input_lay',u'Cat\xe1logo CENFEMUL',"Input",'GPFeatureLayer',"Required")
		pm4 = Parameter('input_cat',u'Cat\xe1logos disponibles',"Input",'String','Required')
		pm0.filter.list = ['xlsx','xls']
		return [pm0,pm1,pm2,pm3,pm4]

	def copy_tables(self,lst):
		for tab in lst:
			copy(join(self.root,u'tables',tab.split('\\')[-1]),tab)

	def mapping_file(self,map_file):
	    try:
	        AddTableView(self.mxd.activeDataFrame,map_file)
	    except:
	        AddLayer(self.mxd.activeDataFrame,map_file,"BOTTOM")
	        RefreshActiveView()
	    RefreshTOC()

	def set_env(self,parameters,process):
		self.fch = datetime.strptime(parameters[1].valueAsText.split(' ')[0],'%d/%m/%Y')
		self.main_dir = join(parameters[2].valueAsText,process)
		mkd(self.main_dir)
		chdir(self.main_dir)
		try:
			copy(parameters[0].valueAsText,self.main_dir)
		except:
			pass
		mkd('FINAL')
		chdir('FINAL')
		env.workspace = getcwd()
		env.overwriteOutput = True
		mklistdir(['CARTO2010','PRODUCTOS_COMITE'])

	def chk_coor(self,coor):
		if len(coor[0]) < 4 or coor[0].isupper() or len(coor[1]) < 4 or coor[1].isupper() or float(coor[0]) < 14 or float(coor[1]) > -86:
			return [u'0',u'0']
		else:
			if float(coor[0]) > 35:
				coor[0] = coor[0][:2]+u'.'+coor[0][2:].split('.')[0]
			if float(coor[1]) < -120:
				if coor[1][:2] == '-1':
					coor[1] = coor[1][:4]+u'.'+coor[1][4:-1].split('.')[0]
				else:
					coor[1] = coor[1][:3]+u'.'+coor[1][3:-1].split('.')[0]
			return coor

	def chk_cvs(self,messages,fields):
		with SearchCursor(self.tab,fields) as sc:
			cvs = [[cve[0],u'Baja'] if cve[1] == u'B' else [cve[0],u'Inexistente'] for cve in sc if len(cve[1]) != 9]
			if len(cvs) != 0:
				with open('Reporte_de_claves_invalidas.txt', 'w') as txt:
					txt.write("Las siguientes claves no se encontraron en el catálogo de localidades vigente a la fecha seleccionada\n".encode('cp1254'))
					for c in cvs:
						txt.write("\nClave: {0}\t Estatus: {1}".format(c[0],c[1]))
					messages.addWarningMessage("Se encontraron claves de localidad invalidas:\nSe creó el archivo: Reporte_de_claves_invalidas.txt\nEn {0}".format(getcwd()))

	def update_dbf(self,parameters):
		cenf = Layer(parameters[3].valueAsText)
		AddJoin_management(self.tab,"CVE_LOCC",cenf.name,"CVE_LOCC","KEEP_COMMON")
		expr = """def calc(fld1,fld2):
			if fld1 == 0:
				return fld2
			else:
				return fld1"""
		CalculateField_management(self.tab,"{0}.LATITUD".format(self.tab.name),"calc(!{0}.LATITUD!,!{1}.LAT_DEC!)".format(self.tab.name,cenf.name),"PYTHON",expr)
		CalculateField_management(self.tab,"{0}.LONGITUD".format(self.tab.name),"calc(!{0}.LONGITUD!,!{1}.LON_DEC!)".format(self.tab.name,cenf.name),"PYTHON",expr)
		SelectLayerByAttribute_management(self.tab,"NEW_SELECTION",""" "{0}.CVE_ORI" <> "{0}.CVE_LOCC" """.format(self.tab.name))
		CalculateField_management(self.tab,"{0}.NOM_LOC".format(self.tab.name),"!{0}.NOM_LOC!".format(cenf.name),"PYTHON")
		SelectLayerByAttribute_management(self.tab,"CLEAR_SELECTION")
		RemoveJoin_management(self.tab)
		DeleteField_management(self.tab,u"CVE_ORI")

	def make_shp(self,parameters,format):
		fecha = self.fch.strftime(format)
		sr = SpatialReference()
		sr.loadFromString(u"PROJCS['Lambert',GEOGCS['GCS_ITRF_1992',DATUM['D_ITRF_1992',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-102.0],PARAMETER['Standard_Parallel_1',17.5],PARAMETER['Standard_Parallel_2',29.5],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',12.0],UNIT['Meter',1.0]];-37031600 -25743800 113924041.206794;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
		MakeXYEventLayer_management(self.tab,'LONGITUD','LATITUD','Lyr','ITRF 1992')
		Project_management('Lyr','{0}_{1}.shp'.format(self.tab.name,fecha),sr)
		#remove("{0}.dbf".format(self.tab.name))
		self.lyer = Layer('{0}_{1}.shp'.format(self.tab.name,fecha))
		RemoveLayer(self.mxd.activeDataFrame,ListLayers(self.mxd.activeDataFrame,Layer(parameters[3].valueAsText).name)[0])
		inf_object.mapping_file(self,self.lyer)

	def coord_lamb(self):
		CalculateField_management(self.lyer,"X_LAMB","!Shape!.FirstPoint.X","PYTHON_9.3")
		CalculateField_management(self.lyer,"Y_LAMB","!Shape!.FirstPoint.Y","PYTHON_9.3")
from __future__ import unicode_literals, print_function, absolute_import
from .objects import come_comu
from .valids import Valide_E04

__all__ = ["Comedores"]

class Comedores(Valide_E04):
	cc = come_comu()
	def __init__(self):
		self.label = "04-Comedores Comunitarios"
		self.description = ""
		self.category = "05_INFRAESTRUCTURA_SOCIAL"
		self.canRunInBackground = False
		self.cc = Comedores.cc

	def getParameterInfo(self):
		return self.cc.params(u'Base Registral de Comedores Comunitarios')

	def isLicensed(self):
		return self.cc._license

	def execute(self,parameters,messages):
		self.cc.set_env(parameters,u'COMEDORES_COMUNITARIOS')
		self.cc.read_xlsx(parameters[0].valueAsText)
		tab = self.cc.make_dbf()
		self.cc.equivalencias([tab,'CVE_ORI','CVE_LOCC',parameters[4].valueAsText],messages)
		self.cc.chk_cvs(messages,["CVE_ORI","CVE_LOCC"])
		self.cc.update_dbf(parameters)
		self.cc.status()
		self.cc.make_shp(parameters,'%Y%m')
		self.cc.coord_lamb()
		self.cc.carto2010()
		self.cc.productos_c()
		self.cc.copy_tables([u'DICCIONARIO_COMEDORES_COMUNITARIOS.xlsx',u'PRODUCTOS_COMITE\\DICCIONARIO_COMEDORES_COMUNITARIOS_CONFIDENCIALIDAD.xlsx'])
		self.cc.barrendero
		return
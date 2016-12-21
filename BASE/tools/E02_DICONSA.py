from __future__ import unicode_literals, print_function, absolute_import
from .objects import dicon
from .valids import Valide_E02

__all__ = ["DICONSA"]

class DICONSA(Valide_E02):
	d = dicon()
	def __init__(self):
		self.label = "02-DICONSA"
		self.description = ""
		self.category = "05_INFRAESTRUCTURA_SOCIAL"
		self.canRunInBackground = False
		self.d = DICONSA.d

	def getParameterInfo(self):
		return self.d.params(u'Directorio nacional de tiendas DICONSA')+self.d.pms_ad

	def isLicensed(self):
		return self.d._license

	def execute(self,parameters,messages):
		self.d.set_env(parameters,u'DICONSA')
		self.d.read_xlsx(parameters,messages)
		tab = self.d.make_dbf()
		self.d.equivalencias([tab,u'CVE_LOCC1',u'CVE_ACT',parameters[4].valueAsText],messages)
		self.d.chk_cvs(messages,["CVE_LOCC1","CVE_ACT"])
		self.d.update_dbf(parameters)
		self.d.make_shp(parameters,'%m%y')
		self.d.coord_lamb()
		self.d.shp_fin()
		self.d.carto2010()
		self.d.productos_c()
		self.d.copy_tables([u'DICCIONARIO_DE_DATOS_DICONSA.xlsx'])
		self.d.barrendero
		return
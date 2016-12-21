from __future__ import unicode_literals, print_function, absolute_import
from .objects import estans_inf
from .valids import Valide_E03

__all__ = ["Estancias"]

class Estancias(Valide_E03):
	ei = estans_inf()
	def __init__(self):
		self.label = "03-Estancias Infantiles"
		self.description = ""
		self.category = "05_INFRAESTRUCTURA_SOCIAL"
		self.canRunInBackground = False
		self.ei = Estancias.ei

	def getParameterInfo(self):
		return self.ei.params(u'Estancias Infantiles')

	def isLicensed(self):
		return self.ei._license

	def execute(self,parameters,messages):
		self.ei.set_env(parameters,u'ESTANCIAS_INFANTILES')
		self.ei.read_xlsx(parameters)
		tab = self.ei.make_dbf()
		self.ei.equivalencias([tab,u'CVE_ORI',u'CVE_LOCC',parameters[4].valueAsText],messages)
		self.ei.chk_cvs(messages,["CVE_ORI","CVE_LOCC"])
		self.ei.update_dbf(parameters)
		self.ei.make_shp(parameters,'%m%y')
		self.ei.tab_estandar()
		self.ei.carto2010()
		self.ei.productos_c()
		self.ei.copy_tables([u'ESTRUCTURA_ESTINFANTILES_2016.xlsx'])
		self.ei.barrendero
		return
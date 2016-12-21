from __future__ import unicode_literals, print_function, absolute_import
from .objects import licon
from .valids import Valide_E01

__all__ = ["LICONSA"]

class LICONSA(Valide_E01):
	l = licon()
	def __init__(self):
		self.label = "01-LICONSA"
		self.description = ""
		self.category = "05_INFRAESTRUCTURA_SOCIAL"
		self.canRunInBackground = False
		self.l = LICONSA.l

	def getParameterInfo(self):
		return self.l.pms_ad+self.l.params('')[1:]

	def isLicensed(self):
		return self.l._license

	def execute(self,parameters,messages):
		self.l.set_env(parameters,u'LICONSA')
		self.l.copy_shp(parameters)
		lyer = self.l.set_shp(parameters)
		self.l.equivalencias([lyer,u'CVE_LOCC',u'CVE_ACT',parameters[4].valueAsText],messages)
		self.l.update_shp(parameters)
		self.l.carto2010()
		self.l.productos_c()
		self.l.sin_cc()
		self.l.copy_tables([u'DICC_DE_VARIABLES_LICONSA_COMPLETO_21SEP16.xls',u'SIN_CAMPOS_CONFIDENCIALES\\DICC_VARIABLES_LIC_SIN_CAMPOS_CONFIDENCIALES_21SEP16.xlsx'])
		self.l.barrendero
		return
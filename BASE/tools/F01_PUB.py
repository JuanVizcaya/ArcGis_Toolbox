from __future__ import unicode_literals, print_function, absolute_import
from .objects import pub
from .valids import Valide_F01

__all__ = ["PUB"]

class PUB(Valide_F01):
	p = pub()
	def __init__(self):
		self.label = "01_PUB"
		self.description = ""
		self.category = "06-PRESENCIA"
		self.canRunInBackground = False
		self.p = PUB.p

	def getParameterInfo(self):
		return self.p.params

	def isLicensed(self):
		return self.p._license

	def execute(self,parameters,messages):
		self.p.set_env(parameters)
		for table in parameters[2].values:
			self.p.fld_2_dbf(table)
			self.p.equivalencias([table.value,"CVE_LOCC","CVE_ACT",parameters[3].valueAsText],messages)
			self.p.dbf_treatment()
			self.p.make_agreg()
		for sheet in parameters[1].values:
			self.p.sheet_comp(messages,sheet)
		self.p.save_book()
from __future__ import unicode_literals, print_function, absolute_import
from .objects import sepomex
from .valids import Valide_C01

__all__ = ["Sepo"]

class Sepo(Valide_C01):
    sep = sepomex()
    def __init__(self):
        self.label = "01-SEPOMEX"
        self.description = ""
        self.category = "03_SEPOMEX"
        self.canRunInBackground = False
        self.sep = Sepo.sep

    def getParameterInfo(self):
        return self.sep.params

    def isLicensed(self):
        return self.sep._license

    def execute(self, parameters, messages):
        self.sep.process(parameters)
        return
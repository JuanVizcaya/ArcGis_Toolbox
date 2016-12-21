from __future__ import unicode_literals, print_function, absolute_import
from .objects import obc
from .valids import Valide_B02

__all__ = ["COORD"]

class COORD(Valide_B02):
    def __init__(self):
        self.label = "02-Proceso de Coordenadas"
        self.description = ""
        self.category = "02_CENFEMUL"
        self.canRunInBackground = False
        self.c = obc()

    def getParameterInfo(self):
        return self.c.params

    def execute(self, parameters, messages):
    	self.c.execute(parameters,messages)
        return
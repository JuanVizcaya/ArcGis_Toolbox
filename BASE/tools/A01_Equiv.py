from __future__ import unicode_literals, print_function, absolute_import
from .objects import calc_equiv
from .valids import Valide_A01

__all__ = ["EQV"]

class EQV(Valide_A01):
    e = calc_equiv()
    def __init__(self):
        self.label = "01-CALCULAR"
        self.description = ""
        self.category = "01_EQUIVALENCIAS"
        self.canRunInBackground = False
        self.e = EQV.e

    def getParameterInfo(self):
        return self.e.params

    """def updateParameters(self,parameters):
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
        return"""

    def isLicensed(self):
        return self.e._license

    def execute(self, parameters, messages):
        self.e.equivalencias([parameters[0].valueAsText,parameters[1].valueAsText,parameters[2].valueAsText,parameters[3].valueAsText],messages)
        return
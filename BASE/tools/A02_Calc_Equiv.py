from __future__ import unicode_literals, print_function, absolute_import
from .objects import act_equiv
from .valids import Valide_A02

__all__ = ["ACT_EQV"]

class ACT_EQV(Valide_A02):
    def __init__(self):
        self.label = "02-ACTIALIZAR_EQUIVALENCIAS"
        self.description = ""
        self.category = "01_EQUIVALENCIAS"
        self.canRunInBackground = False
        self.a = act_equiv()

    def getParameterInfo(self):
        return self.a.params

    def isLicensed(self):
        return self.a._license

    def execute(self, parameters, messages):
        self.a.actualiza([i.valueAsText for i in parameters],messages)
        return
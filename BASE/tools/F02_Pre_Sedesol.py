from __future__ import unicode_literals, print_function, absolute_import
from .objects import pre_s
from .valids import Valide_F02

__all__ = ["Pre_SEDESOL"]

class Pre_SEDESOL(Valide_F02):
    PS = pre_s()
    def __init__(self):
        self.label = "02_SEDESOL"
        self.description = ""
        self.category = "06-PRESENCIA"
        self.canRunInBackground = False
        self.PS = Pre_SEDESOL.PS

    def getParameterInfo(self):
        return self.PS.parameters

    def isLicensed(self):
        return self.PS._license

    def execute(self, parameters, messages):
        self.PS.set_workspace(parameters[0].valueAsText,messages)
        self.PS.add_fields(parameters[0].valueAsText,messages)
        self.PS.equivalencias([parameters[0].valueAsText,"CVE_LOC","CVE_ACT",parameters[4].valueAsText],messages)
        self.PS.fill(parameters[0].valueAsText,messages)
        self.PS.comp_values(parameters[1].valueAsText,parameters[2].value,parameters[3].valueAsText,messages)
        return
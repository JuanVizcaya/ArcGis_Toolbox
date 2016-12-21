from __future__ import unicode_literals, print_function, absolute_import
from .objects import siipso
from .valids import Valide_B04

__all__ = ["SIIPSO"]

class SIIPSO(Valide_B04):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "04-Proceso SIIPSO"
        self.description = ""
        self.category = "02_CENFEMUL"
        self.canRunInBackground = False
        self.s = siipso()

    def getParameterInfo(self):
        """Define parameter definitions"""
        return  self.s.my_parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return self.s._license

    def execute(self, parameters, messages):
        """The source code of the tool."""
        self.s.execute([i.valueAsText for i in parameters],messages)
        return
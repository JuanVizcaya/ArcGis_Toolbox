from __future__ import unicode_literals, print_function, absolute_import
from .objects import cat_loc
from .valids import Valide_B03

__all__ = ["CAT_LOC"]

class CAT_LOC(Valide_B03):
    def __init__(self):
        self.label = "03-Proceso cat_loc"
        self.description = ""
        self.category = "02_CENFEMUL"
        self.canRunInBackground = False
        self.c = cat_loc()

    def getParameterInfo(self):
        return self.c.params

    def execute(self, parameters, messages):
        self.c.execute(parameters, messages)
        return
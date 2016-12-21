from __future__ import unicode_literals, print_function, absolute_import
from .objects import est_cenf
from .valids import Valide_B01

__all__ = ["Estand_CENF"]

class Estand_CENF(Valide_B01):
    def __init__(self):
        self.label = "01-ESTANDARIZAR"
        self.description = ""
        self.category = "02_CENFEMUL"
        self.canRunInBackground = False
        self.est = est_cenf()

    def getParameterInfo(self):
        return self.est.params

    def isLicensed(self):
        return self.est._license

    def execute(self, parameters, messages):
        dwnl_dir = self.est.Makedir(parameters)
        if parameters[8].value:
            self.est.dwnl_cats(dwnl_dir)
        for arch,tipo in zip([parameters[0],parameters[9],parameters[2],parameters[4]],[0,1,2,3]):
            if arch.value:
                tab = self.est.Stand(arch.valueAsText,tipo,parameters)
                if tipo in [0,1] and parameters[7].value:
                    self.est.mkshape()
        if parameters[9].value:
            self.est.copy2ps()
        if parameters[10].value:
            self.est.report()
        self.est.barrendero
        return
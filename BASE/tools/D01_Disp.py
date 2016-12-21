# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function, absolute_import
from .objects import disp_movil, AYB
from .valids import Valide_D01, Valide_D02, Valide_D03
from os import chdir

__all__ = ["Archs_DM", "Dispos", "AyB_DM"]

class Archs_DM(Valide_D01):
    adm = disp_movil()
    def __init__(self):
        self.label = "01-Recopila archivos"
        self.description = ""
        self.category = "04_DISPOSITIVOS_MOVILES"
        self.canRunInBackground = False
        self.adm = Archs_DM.adm

    def getParameterInfo(self):
        return self.adm.params_recarch

    def isLicensed(self):
        return self.adm._license

    def execute(self, parameters, messages):
        self.adm.makindir(parameters)
        cvs = self.adm.set_sum(parameters)
        self.adm.equivalencias([cvs,"CVE_LOC","CVE_ACT",parameters[4].valueAsText],messages)
        self.adm.locsiter(parameters,cvs)
        self.adm.map_all()
        return

class Dispos(Valide_D02):
    def __init__(self):
        self.label = u"02-Proceso a catálogos".encode("cp1254")
        self.description = ""
        self.category = "04_DISPOSITIVOS_MOVILES"
        self.canRunInBackground = False
        self.dm = disp_movil()

    def getParameterInfo(self):
        return self.dm.params_process

    def isLicensed(self):
        return self.dm._license

    def execute(self, parameters, messages):
        if parameters[0].value:
            self.dm.localidad(parameters)
        if parameters[1].value:
            self.dm.agebs(parameters)
        if parameters[2].value:
            self.dm.manzanas(parameters)
        if parameters[3].value:
            self.dm.cps(parameters)
        if parameters[4].value:
            self.dm.asentamientos(parameters)
        if parameters[5].value:
            self.dm.vialidades(parameters)
        self.dm.barrendero(parameters[6].valueAsText)
        return

class AyB_DM(Valide_D03):
    def __init__(self):
        self.label = u"03-Altas y bajas de catálogos".encode('cp1254')
        self.description = ""
        self.category = "04_DISPOSITIVOS_MOVILES"
        self.canRunInBackground = False
        self.ayb = AYB()

    def getParameterInfo(self):
        return self.ayb.params

    def isLicensed(self):
        return self.ayb._license

    def execute(self, parameters, messages):
        chdir(parameters[6].valueAsText)
        self.ayb.ageb_movs(parameters)
        self.ayb.ageb_bajas()
        self.ayb.ageb_altas(parameters[3].valueAsText)
        self.ayb.mzs_bajas(parameters[4].valueAsText)
        self.ayb.mzs_altas(parameters[5].valueAsText)
        self.ayb.barrendero
        return
from __future__ import unicode_literals, print_function, absolute_import
from arcpy.da import SearchCursor, UpdateCursor
from arcpy import Parameter, Exists, ListFields, CalculateField_management, SetProgressor, GetCount_management, SetProgressorLabel, SetProgressorPosition
from os.path import join
from .utils import checkdate, unzip, readFromObj
from .data import bar

__all__ = ["calc_equiv"]

class calc_equiv(object):
    def __init__(self):
        self.__licens = "users"
        self.path = bar.fpath

    @property
    def _license(self):
        return True
        #return utils.license_v2(utils.licens.lists[self.__licens])
    
    @property
    def params(self):
        table = Parameter('input_tab',u'Tabla con claves geostad\xedsticas',"Input","GPTableView","Required")
        field_ori = Parameter('input_fld1',u'CVELOCC_ORI',"Input",'Field','Required')
        field_ori.filter.list = ['Text']
        field_ori.parameterDependencies = [table.name]
        field_act = Parameter('input_fld2',u'CVELOCC_ACT',"Input",'Field','Required')
        field_act.filter.list = ['Text']
        field_act.parameterDependencies = [table.name]
        cat_list = Parameter('input_cat',u'Cat\xe1logos disponibles',"Input",'String','Required')
        return [table,field_ori,field_act,cat_list]

    def updateOpc(self):
        self.dic = checkdate(bar.cats)
        #self.ms = sorted(self.dic.keys(),reverse = True)
        self.ms = self.dic.keys()

    def updateEqv(self):
        unzip(join(self.path,"A0EQV01.eqvz"))
        self.cve_eqv = readFromObj(join(self.path,"edata.eqv"))

    def updateCat(self,cat):
        unzip(join(self.path,self.dic[cat]))
        self.cve_loc = readFromObj(join(self.path,"cdata.cat"))
        self.cve_eqv = [cves for cves in self.cve_eqv if int(cves[3].replace('-','')[:6]) <= int(self.dic[cat][:6])]

    def equivalencias(self,parameters,messages):
        CalculateField_management(parameters[0],parameters[2],"!{0}!".format(parameters[1]),"PYTHON")
        i = 0
        with SearchCursor(parameters[0],[parameters[1],parameters[2]]) as sc:
            self.cve_ori = [row[0] for row in sc]
        setori = set(self.cve_ori)
        setloc = set(self.cve_loc)
        isn = setori.difference(setloc)
        if len(isn) > 0:
            cla = u'"{1}" IN ({0})'.format(u",".join([u"'{0}'".format(st) for st in isn]),parameters[1])
            SetProgressor("step",'Start',0,len(isn),1)
        elif len(isn) == 0:
            cla = None
            SetProgressor("step",'Start',0,int(GetCount_management(parameters[0])[0]),1)
        #utils.arcpy.SetProgressor("step",'Start',0,int(utils.arcpy.GetCount_management(parameters[0])[0]),1)
        with UpdateCursor(parameters[0],[parameters[1],parameters[2]],cla) as uc: #cla delete
            for loc in uc:
                locc = loc[0]
                if locc in self.cve_loc:
                    #loc[1] = locc
                    #uc.updateRow(loc)
                    paco = True
                else:
                    paco = False
                while not paco:
                    fch = sorted([row for row in self.cve_eqv if row[0] == locc or row[1] == locc], key = lambda x:x[3],reverse=True)
                    if len(fch) > 0:
                        fch = fch[0][3]
                        for ren in [row for row in self.cve_eqv if (row[0] == locc or row[1] == locc) and row[3] == fch]:
                            if ren[2] in [u'BAJA DE LOCALIDAD POR SER SERVICIO',u'INEXISTENTE',u'TAPIA O RUINAS']:
                                loc[1] = 'B'
                                paco = True
                                uc.updateRow(loc)
                                break
                            if ren[2] in [u'CAMBIO DE \xc1MBITO',u'CAMBIO DE NOMBRE',u'CREACI\xd3N DE LOCALIDAD',u'REACTIVACI\xd3N DE LOCALIDAD',u'DESCONURBADA',u'DESFUSIONADA']:
                                pass
                            """if ren[2] in [u'DESCONURBADA',u'DESFUSIONADA']:
                                if ren[1] in self.cve_loc:
                                    locc = ren[0]
                                    if locc in self.cve_loc:
                                        loc[1] = locc
                                        uc.updateRow(loc)
                                        paco = True
                                        break
                                else:
                                    pass"""
                            if ren[2] in [u'CONURBACI\xd3N DE LOCALIDAD',u'FUSI\xd3N DE LOCALIDAD',u'LOCALIDAD QUE CAMBIA DE ENTIDAD',u'LOCALIDAD QUE CAMBIA DE MUNICIPIO',u'LOCALIDAD QUE CAMBIA DE MUN. POR NUEVA CREACI\xd3N']:
                                if locc == ren[1]:
                                    locc = ren[0]
                                    if locc in self.cve_loc:
                                        loc[1] = locc
                                        uc.updateRow(loc)
                                        paco = True
                                        break
                    else:
                        loc[1] = u""
                        messages.addWarningMessage(u"la clave: {0} no se encontr\xf3 en tabla de equivalencias".format(locc))
                        paco = True
                        uc.updateRow(loc)
                        break
                SetProgressorLabel (u"{0}".format(locc))
                i+=1
                SetProgressorPosition(i)        
        return
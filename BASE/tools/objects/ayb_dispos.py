# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function
from arcpy import AddJoin_management, AddField_management, mapping, RefreshTOC, Parameter, CalculateField_management,RemoveJoin_management, DeleteField_management,Statistics_analysis
from arcpy.da import SearchCursor, InsertCursor
from utils import mktable
from datetime import datetime, timedelta
from os.path import join
from os import getcwd, walk, remove

__all__ = ["AYB"]

class AYB(object):
    def __init__(self):
        self.__licens = "users"

    @property
    def _license(self):
    	return True
        #return utils.license_v2(utils.licens.lists[self.__licens])

    @property
    def params(self):
    	pm0 = Parameter('tab_vig',u'Cat\xe1logo agebs vigente','Input','GPTableView','Required')
    	pm1 = Parameter('tab_iter',u'locsiter10vscenfemul actual:','Input','GPTableView','Required')
    	pm2 = Parameter('tab_loc',u'cat_localidad_completo actual:','Input','GPTableView','Required')
        pm3 = Parameter('tab_agebs',u'cat\xe1logo de agebs actual:','Input','GPTableView','Required')
        pm4 = Parameter('tab_mzs',u'cat\xe1logo de manzanas vigente:','Input','GPTableView','Required')
        pm5 = Parameter('tab_agebact',u'cat\xe1logo de manzanas actual:','Input','GPTableView','Required')
    	pm6 = Parameter('savedir',u'ruta de salida:','Input','DEWorkspace','Required')
        pm7 = Parameter('Fecha_actual',u'Fecha de actualización (dd/mm/aaaa):'.encode('cp1254'),'Input','GPDate','Required')
    	return [pm0,pm1,pm2,pm3,pm4,pm5,pm6,pm7]

    @property
    def barrendero(self):
        for root, dirs, files in walk(".", topdown=False):
            for name in files:
                    if name.endswith('.xml') or name.endswith('borrar.dbf'):
                            remove(join(root, name))
        return

    def mapping_tab(self,tabla):
        mxd = mapping.MapDocument("CURRENT")
        df = mapping.ListDataFrames(mxd,"*")[0]
        mapping.AddTableView(df,tabla)
        RefreshTOC()
        return

    def ageb_movs(self,parameters):
        self.fech_act = datetime.strptime(parameters[7].valueAsText,'%d/%m/%Y')
        AddField_management(parameters[0].valueAsText,*[u"CVE_LOCC","TEXT",0,0,9])
        CalculateField_management(parameters[0].valueAsText,"CVE_LOCC","!CVE_AGEB![:9]","PYTHON")
        AddJoin_management(parameters[0].valueAsText,"CVE_LOCC",parameters[1].valueAsText,"CVE_ITER10","KEEP_ALL")
        AddJoin_management(parameters[0].valueAsText,"locsiter10vscenfemul.CVECEFEMUL",parameters[2].valueAsText,"CVE_LOCC","KEEP_ALL")
        fields = ["{0}.C_AGEB".format(parameters[0].valueAsText),"{0}.CVE_AGEB".format(parameters[0].valueAsText),"{0}.C_LOCALI".format(parameters[0].valueAsText),"{0}.FCH_INICIO".format(parameters[0].valueAsText),"{0}.FCH_FINAL".format(parameters[0].valueAsText),"cat_localidad_completo.ID_LOC"]
        with SearchCursor(parameters[0].valueAsText,fields) as sc:
            self.movs = [row for row in sc if row[2] != str(row[5])[:9]]
        RemoveJoin_management(parameters[0].valueAsText)
        DeleteField_management(parameters[0].valueAsText,u"CVE_LOCC")
        return

    def ageb_bajas(self):
        flds = [[u'C_AGEB',"LONG",6,0,0],[u'CVE_AGEB',"TEXT",0,0,13],[u'C_LOCALI',"TEXT",0,0,9],[u'FCH_INICIO',"DATE",0,0,9],[u'FCH_FINAL',"DATE",0,0,9]]
        self.tab_bajas = mktable('bajas_cat_agebs_{0}.dbf'.format(self.fech_act.strftime('%b%y')),flds)
        with InsertCursor(self.tab_bajas,[fld[0] for fld in flds]) as ic:
            for row in self.movs:
                ic.insertRow((row[0],row[1],row[2],row[3],self.fech_act))
        AYB.mapping_tab(self,self.tab_bajas)
        return

    def ageb_altas(self,tab_agebs):
        AddJoin_management(self.tab_bajas,u"CVE_AGEB",tab_agebs,u"AGEB","KEEP_COMMON")
        with SearchCursor(self.tab_bajas,"*") as sc:
            datos = [row[7:] for row in sc]
        RemoveJoin_management(self.tab_bajas)
        flds = [[u'ID_LOC',"DOUBLE",13,0,0],[u'AGEB',"TEXT",0,0,13],[u'AGEB_ID',"LONG",9,0,0],[u'MUN_ID',"LONG",5,0,0],[u'ENTIDAD_ID',"SHORT",2,0,0],[u'FCH_INICIO',"DATE",0,0,9]]
        tab_altas = mktable('altas_cat_agebs_{0}.dbf'.format(self.fech_act.strftime('%b%y')),flds)
        with InsertCursor(tab_altas,[fld[0] for fld in flds]) as ic:
            for row in datos:
                ic.insertRow(row+(self.fech_act,))
        AYB.mapping_tab(self,tab_altas)
        return

    def mzs_bajas(self,tab_mzs):
        Statistics_analysis(self.tab_bajas,join(getcwd(),u'Sumarize_bajageb_borrar.dbf'),[[u"C_AGEB","COUNT"]],u"C_AGEB")
        tab_sum = mapping.TableView('Sumarize_bajageb_borrar.dbf')
        AddJoin_management(tab_mzs,u"C_AGEB",tab_sum,u"C_AGEB","KEEP_COMMON")
        with SearchCursor(tab_mzs,"*") as sc:
            bajas = [row[1:5] for row in sc]
        RemoveJoin_management(tab_mzs)
        flds = [[u'C_MANZANA',"LONG",7,0,0],[u'CVE_MANZAN',"TEXT",0,0,16],[u'C_AGEB',"LONG",6,0,0],[u'FCH_INICIO',"DATE",0,0,9],[u'FCH_FINAL',"DATE",0,0,9]]
        self.tab_mzb = mktable('bajas_cat_manzanas_{0}.dbf'.format(self.fech_act.strftime('%b%y')),flds)
        with InsertCursor(self.tab_mzb,[fld[0] for fld in flds]) as ic:
            for row in bajas:
                ic.insertRow(row+(self.fech_act,))
        AYB.mapping_tab(self,self.tab_mzb)
        return

    def mzs_altas(self,tab):
        tab_mzact = mapping.TableView(tab)
        Statistics_analysis(self.tab_mzb,join(getcwd(),u'Sumarize_bajamzs_borrar.dbf'),[[u"CVE_MANZAN","COUNT"]],u'CVE_MANZAN')
        tab_sum = mapping.TableView('Sumarize_bajamzs_borrar.dbf')
        AddJoin_management(tab_mzact,"CVE_MZAC",self.tab_mzb,"CVE_MANZAN","KEEP_COMMON")
        with SearchCursor(tab_mzact,"*") as sc:
            altas = [row[1:10] for row in sc]
        flds = [[u'AGEB_ID',"LONG",9,0,0],[u'CVE_MZAC',"TEXT",0,0,16],[u'MANZANA_ID',"LONG",9,0,0],[u'ENTIDAD_ID',"SHORT",2,0,0],[u'MANZANA',"TEXT",0,0,3],[u'MUN_ID',"LONG",5,0,0],[u'CVE_LOCNUM',"SHORT",4,0,0],[u'CVE_LOCC',"TEXT",0,0,9],[u'AGEB',"TEXT",0,0,5],[u'FCH_INICIO',"DATE",0,0,9]]
        tab_mzal = mktable('altas_cat_manzanas_{0}.dbf'.format(self.fech_act.strftime('%b%y')),flds)
        with InsertCursor(tab_mzal,[fld[0] for fld in flds]) as ic:
            for row in altas:
                ic.insertRow(row+(self.fech_act,))
        AYB.mapping_tab(self,tab_mzal)
        return
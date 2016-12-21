from __future__ import unicode_literals, print_function, absolute_import
import os
import arcpy
from .utils import today, readFromStr, mkd, mth_ant, change_format, pickle

__all__ = ["siipso"]

class siipso(object):
    def __init__(self):
        #self.__url = 'https://raw.githubusercontent.com/dgaae/data/master'
        self.__path = os.path.dirname(__file__)
        self.deposit_path = os.path.dirname(os.path.abspath(__file__))
        self.__licens = "users"
        self.flm = arcpy.FieldMappings()
        self.today = today().lower()
        self.fields = [(u'CVE_LOCALI', u"TEXT", 0, 0, 9), (u'NOM_LOCALI', u"TEXT", 0, 0, 110), (u'FCH_INICIO', u"DATE"), (u'C_MUNICIPI', u"LONG", 5, 0, 5), (u'LATITUD', u"TEXT", 0, 0, 10), (u'LONGITUD', u"TEXT", 0, 0, 11), (u'ALTITUD', u"TEXT", 0, 0, 4), (u'P_TOTAL', u"DOUBLE", 11, 0, 11), (u'P_MAS', u"DOUBLE", 11, 0, 11), (u'P_FEM', u"DOUBLE", 11, 0, 11), (u'V_TOT', u"DOUBLE", 11, 0, 11)]
        #self.munici = readFromStr('https://raw.githubusercontent.com/dgaae/data/master/data/C0MUN01.muns')
        arcpy.env.overwriteOutput = True


    @property
    def _license(self):
        #return _utils.license("{0}/licens/{1}.lic".format(self.__url,self.__licens))
        return True

    @property
    def my_parameters(self):
        param0 = arcpy.Parameter('input_cat','Catalogo CENFEMUL',"Input",'GPFeatureLayer','Required')
        param1 = arcpy.Parameter('input_eqv','Tabla de equivalencias',"Input",'GPTableView','Required')
        param2 = arcpy.Parameter('input_loc','LOC_ACT mes anterior',"Input",'GPTableView','Required')
        return [param0,param1,param2]

    def execute(self, parameters, messages):
        self.mxd = arcpy.mapping.MapDocument("CURRENT")
        lyr = arcpy.mapping.ListLayers(self.mxd,parameters[0],self.mxd.activeDataFrame)[0]
        tab = arcpy.mapping.ListTableViews(self.mxd,parameters[1],self.mxd.activeDataFrame)[0]
        loc = arcpy.mapping.ListTableViews(self.mxd,parameters[2],self.mxd.activeDataFrame)[0]
        path = os.path.dirname(lyr.workspacePath)
        mkd(os.path.join(path,"PROCESO_SIIPSO"))
        arcpy.env.workspace = os.path.join(path,"PROCESO_SIIPSO")
        with arcpy.da.SearchCursor(tab,"FECHA_ACT") as sc:
            fch = [row[0] for row in sc]
        fch.sort(reverse = True)
        fch = fch[0]
        arcpy.TableToTable_conversion(tab,arcpy.env.workspace,"tabequiv_{0}.dbf".format(tab.name[-5:].lower()),""""FECHA_ACT" = '{0}'""".format(fch))
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,tab)
        arcpy.RefreshTOC()
        tab = arcpy.mapping.TableView("tabequiv_{0}.dbf".format(tab.name[-5:].lower()))
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,tab)
        arcpy.RefreshTOC()
        tab = arcpy.mapping.ListTableViews(self.mxd,tab.name,self.mxd.activeDataFrame)[0]
        arcpy.AddJoin_management(lyr,"CVE_LOCC",loc,"CVE_LOC")
        arcpy.SelectLayerByAttribute_management(lyr,"NEW_SELECTION",""""{0}.CVE_LOC" IS NULL""".format(loc.name))
        altas = int(arcpy.GetCount_management(lyr)[0])
        self.flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},{0}.CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},{0}.CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},{0}.CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},{0}.NOM_ENT,-1,-1;ABR_ENT "ABR_ENT" true true false 16 Text 0 0 ,First,#,{0},{0}.ABR_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},{0}.NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},{0}.NOM_LOC,-1,-1;AMBITO "AMBITO" true true false 1 Text 0 0 ,First,#,{0},{0}.AMBITO,-1,-1;CVE_CARTA "CVE_CARTA" true true false 6 Text 0 0 ,First,#,{0},{0}.CVE_CARTA,-1,-1;PLANO "PLANO" true true false 1 Text 0 0 ,First,#,{0},{0}.PLANO,-1,-1;LATITUD "LATITUD" true true false 10 Text 0 0 ,First,#,{0},{0}.LATITUD,-1,-1;LONGITUD "LONGITUD" true true false 11 Text 0 0 ,First,#,{0},{0}.LONGITUD,-1,-1;LAT_DEC "LAT_DEC" true true false 13 Double 8 12 ,First,#,{0},{0}.LAT_DEC,-1,-1;LON_DEC "LON_DEC" true true false 15 Double 8 14 ,First,#,{0},{0}.LON_DEC,-1,-1;ALTITUD "ALTITUD" true true false 4 Text 0 0 ,First,#,{0},{0}.ALTITUD,-1,-1;P_TOTAL "P_TOTAL" true true false 11 Double 0 11 ,First,#,{0},{0}.P_TOTAL,-1,-1;P_MAS "P_MAS" true true false 11 Double 0 11 ,First,#,{0},{0}.P_MAS,-1,-1;P_FEM "P_FEM" true true false 11 Double 0 11 ,First,#,{0},{0}.P_FEM,-1,-1;V_TOT "V_TOT" true true false 11 Double 0 11 ,First,#,{0},{0}.V_TOT,-1,-1'.format(lyr.name))
        arcpy.TableToTable_conversion(lyr,arcpy.env.workspace,"{0}locs_alta_siipso_sinrenombradas.dbf".format(altas),None,self.flm)
        arcpy.SelectLayerByAttribute_management(lyr,"ADD_TO_SELECTION",'"{0}.NOM_LOC" <> "{1}.NOM_LOC"'.format(lyr.name,loc.name))
        altas_con_renom = int(arcpy.GetCount_management(lyr)[0])
        arcpy.TableToTable_conversion(lyr,arcpy.env.workspace,"{0}locs_altas_con_renombradas.dbf".format(altas_con_renom),None,self.flm)
        arcpy.RemoveJoin_management(lyr)
        arcpy.AddJoin_management(loc,"CVE_LOC",lyr,"CVE_LOCC")
        arcpy.SelectLayerByAttribute_management(loc,"NEW_SELECTION",""""{0}.CVE_LOCC" IS NULL""".format(lyr.name))
        bajas = int(arcpy.GetCount_management(loc)[0])
        self.flm.removeAll()
        self.flm.loadFromString(u'C_MUN "C_MUN" true true false 5 Text 0 0 ,First,#,{0},{0}.C_MUN,-1,-1;C_LOC "C_LOC" true true false 10 Text 0 0 ,First,#,{0},{0}.C_LOC,-1,-1;CVE_ENT "CVE_ENT" true true false 3 Text 0 0 ,First,#,{0},{0}.CVE_ENT,-1,-1;CVE_MUN "CVE_MUN" true true false 5 Text 0 0 ,First,#,{0},{0}.CVE_MUN,-1,-1;CVE_LOC "CVE_LOC" true true false 10 Text 0 0 ,First,#,{0},{0}.CVE_LOC,-1,-1;NOM_ENT "NOM_ENT" true true false 35 Text 0 0 ,First,#,{0},{0}.NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 100 Text 0 0 ,First,#,{0},{0}.NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 100 Text 0 0 ,First,#,{0},{0}.NOM_LOC,-1,-1;FCH_INI "FCH_INI" true true false 10 Text 0 0 ,First,#,{0},{0}.FCH_INI,-1,-1;P_TOTAL "P_TOTAL" true true false 15 Text 0 0 ,First,#,{0},{0}.P_TOTAL,-1,-1;P_MAS "P_MAS" true true false 15 Text 0 0 ,First,#,{0},{0}.P_MAS,-1,-1;P_FEM "P_FEM" true true false 15 Text 0 0 ,First,#,{0},{0}.P_FEM,-1,-1;VIV_TOTALS "VIV_TOTALS" true true false 15 Text 0 0 ,First,#,{0},{0}.VIV_TOTALS,-1,-1'.format(loc.name))
        arcpy.TableToTable_conversion(loc,arcpy.env.workspace,"{0}locs_baja_siipso_sinrenombradas.dbf".format(bajas),None,self.flm)
        arcpy.SelectLayerByAttribute_management(loc,"ADD_TO_SELECTION",'"{0}.NOM_LOC" <> "{1}.NOM_LOC"'.format(loc.name,lyr.name))
        bajas_con_renom = int(arcpy.GetCount_management(loc)[0])
        self.flm.removeAll()
        self.flm.loadFromString(u'C_MUN "C_MUN" true true false 5 Text 0 0 ,First,#,{0},{0}.C_MUN,-1,-1;C_LOC "C_LOC" true true false 10 Text 0 0 ,First,#,{0},{0}.C_LOC,-1,-1;CVE_ENT "CVE_ENT" true true false 3 Text 0 0 ,First,#,{0},{0}.CVE_ENT,-1,-1;CVE_MUN "CVE_MUN" true true false 5 Text 0 0 ,First,#,{0},{0}.CVE_MUN,-1,-1;CVE_LOC "CVE_LOC" true true false 10 Text 0 0 ,First,#,{0},{0}.CVE_LOC,-1,-1;NOM_ENT "NOM_ENT" true true false 35 Text 0 0 ,First,#,{0},{0}.NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 100 Text 0 0 ,First,#,{0},{0}.NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 100 Text 0 0 ,First,#,{0},{0}.NOM_LOC,-1,-1;FCH_INI "FCH_INI" true true false 10 Text 0 0 ,First,#,{0},{0}.FCH_INI,-1,-1;P_TOTAL "P_TOTAL" true true false 15 Text 0 0 ,First,#,{0},{0}.P_TOTAL,-1,-1;P_MAS "P_MAS" true true false 15 Text 0 0 ,First,#,{0},{0}.P_MAS,-1,-1;P_FEM "P_FEM" true true false 15 Text 0 0 ,First,#,{0},{0}.P_FEM,-1,-1;VIV_TOTALS "VIV_TOTALS" true true false 15 Text 0 0 ,First,#,{0},{0}.VIV_TOTALS,-1,-1;NOM_LOC_1 "NOM_LOC_1" true true false 110 Text 0 0 ,First,#,{0},{1}.NOM_LOC,-1,-1'.format(loc.name,lyr.name))
        arcpy.TableToTable_conversion(loc,arcpy.env.workspace,"{0}locs_bajas_con_renombradas.dbf".format(bajas_con_renom),None,self.flm)
        arcpy.SelectLayerByAttribute_management(loc,"REMOVE_FROM_SELECTION",""""{0}.CVE_LOCC" IS NULL""".format(lyr.name))
        renombradas = int(arcpy.GetCount_management(loc)[0])
        arcpy.TableToTable_conversion(loc,arcpy.env.workspace,"{0}locs_renombrar_siipso.dbf".format(renombradas),None,self.flm)
        arcpy.RemoveJoin_management(loc)
        arcpy.mapping.RemoveLayer(self.mxd.activeDataFrame,lyr)
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,loc)
        arcpy.RefreshTOC()
        for fol in ("CATALOGO_EMBONADO_CON_CAT_{0}".format(lyr.name[-5:]),"FINAL_A_ENTREGAR_SIIPSO","REVISAR_CATLOCS_SIIPSO","TABLAS_CONTROL_VICKY"):
            mkd(os.path.join(arcpy.env.workspace,fol))
        altas = arcpy.mapping.TableView("{0}locs_altas_con_renombradas.dbf".format(altas_con_renom))
        bajas = arcpy.mapping.TableView("{0}locs_bajas_con_renombradas.dbf".format(bajas_con_renom))
        renom = arcpy.mapping.TableView("{0}locs_renombrar_siipso.dbf".format(renombradas))
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,altas)
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,bajas)
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,renom)
        arcpy.RefreshTOC()
        altas = arcpy.mapping.ListTableViews(self.mxd,altas.name,self.mxd.activeDataFrame)[0]
        bajas = arcpy.mapping.ListTableViews(self.mxd,bajas.name,self.mxd.activeDataFrame)[0]
        renom = arcpy.mapping.ListTableViews(self.mxd,renom.name,self.mxd.activeDataFrame)[0]
        arcpy.env.workspace = os.path.join(arcpy.env.workspace,"TABLAS_CONTROL_VICKY")
        arcpy.env.workspace = os.path.join(path,*("PROCESO_SIIPSO","TABLAS_CONTROL_VICKY"))
        arcpy.TableToTable_conversion(altas,arcpy.env.workspace,"{0}locs_a_dar_de_alta_{1}.dbf".format(altas_con_renom,self.today))
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,altas)
        self.flm.removeAll()
        self.flm.loadFromString(u'C_LOC "C_LOC" true true false 10 Text 0 0 ,First,#,{0},C_LOC,-1,-1;CVE_LOC "CVE_LOC" true true false 10 Text 0 0 ,First,#,{0},CVE_LOC,-1,-1;NOM_LOC "NOM_LOC" true true false 100 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1'.format(bajas.name))
        arcpy.TableToTable_conversion(bajas,arcpy.env.workspace,"{0}locs_a_dar_de_baja_{1}.dbf".format(bajas_con_renom,self.today),None,self.flm)
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,bajas)
        self.flm.removeAll()
        self.flm.loadFromString(u'CVE_LOC "CVE_LOC" true true false 10 Text 0 0 ,First,#,{0},CVE_LOC,-1,-1;NOMLOC_{1} "NOMLOC_{1}" true true false 100 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;NOMLOC_{2} "NOMLOC_{2}" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC_1,-1,-1'.format(renom.name,mth_ant(lyr.name[-5:-2]),lyr.name[-5:-2]))
        arcpy.TableToTable_conversion(renom,arcpy.env.workspace,"{0}locs_a_renombrar_{1}.dbf".format(renombradas,self.today),None,self.flm)
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,renom)
        altas = arcpy.mapping.TableView("{0}locs_a_dar_de_alta_{1}.dbf".format(altas_con_renom,self.today))
        bajas = arcpy.mapping.TableView("{0}locs_a_dar_de_baja_{1}.dbf".format(bajas_con_renom,self.today))
        renom = arcpy.mapping.TableView("{0}locs_a_renombrar_{1}.dbf".format(renombradas,self.today))
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,altas)
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,bajas)
        arcpy.mapping.AddTableView(self.mxd.activeDataFrame,renom)
        arcpy.RefreshTOC()
        altas = arcpy.mapping.ListTableViews(self.mxd,altas.name,self.mxd.activeDataFrame)[0]
        bajas = arcpy.mapping.ListTableViews(self.mxd,bajas.name,self.mxd.activeDataFrame)[0]
        renom = arcpy.mapping.ListTableViews(self.mxd,renom.name,self.mxd.activeDataFrame)[0]
        arcpy.env.workspace = os.path.join(path,*("PROCESO_SIIPSO","FINAL_A_ENTREGAR_SIIPSO"))
        arcpy.AddField_management(renom,"TABEQUIV","SHORT",1)
        arcpy.AddJoin_management(renom,"CVE_LOC",tab,"CVELOCCORI")
        arcpy.SelectLayerByAttribute_management(renom,"NEW_SELECTION",""""{0}.CVELOCCACT" IS NULL""".format(tab.name))
        arcpy.RemoveJoin_management(renom)
        arcpy.CalculateField_management(renom,"TABEQUIV","0","PYTHON")
        arcpy.SelectLayerByAttribute_management(renom,"SWITCH_SELECTION")
        arcpy.CalculateField_management(renom,"TABEQUIV","1","PYTHON")
        arcpy.SelectLayerByAttribute_management(renom,"CLEAR_SELECTION")
        self.flm.removeAll()
        self.flm.loadFromString(u'CVELOC_ACT "CVELOC_ACT" true true false 9 Text 0 0 ,First,#,{0},CVELOCCACT,-1,-1;CVELOC_ANT "CVELOC_ANT" true true false 9 Text 0 0 ,First,#,{0},CVELOCCORI,-1,-1;FCH_INICIO "FCH_INICIO" true true false 8 Date 0 0 ,First,#,{0},FECHA_ACT,-1,-1;TPO_MOVIMI "TPO_MOVIMI" true true false 80 Text 0 0 ,First,#,{0},DESCGO_ACT,-1,-1'.format(tab.name))
        arcpy.TableToTable_conversion(tab,arcpy.env.workspace,"a_loc_movimiento_{0}.dbf".format(tab.name[-5:]),None,self.flm)
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,tab)
        with arcpy.da.UpdateCursor(altas,["CVE_LOCC","NOM_LOC","LATITUD","LONGITUD","ALTITUD","P_TOTAL","P_MAS","P_FEM","V_TOT"]) as uc:
            records = [row for row in uc]
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,altas)
        arcpy.CreateTable_management(arcpy.env.workspace,"a_loc_alta_{0}.dbf".format(tab.name[-5:]))
        altas = arcpy.mapping.TableView("a_loc_alta_{0}.dbf".format(tab.name[-5:]))
        for fld in self.fields:
            arcpy.AddField_management(altas,*fld)
        arcpy.DeleteField_management(altas,"Field1")
        with open(os.path.join(self.deposit_path,'data','C0MUN01.muns'),'r') as muns:
            self.munici = pickle.loads(muns.read())
        with arcpy.da.InsertCursor(altas,[u'CVE_LOCALI', u'NOM_LOCALI', u'C_MUNICIPI', u'LATITUD', u'LONGITUD', u'ALTITUD', u'P_TOTAL', u'P_MAS', u'P_FEM', u'V_TOT']) as ic:
            for row in records:
                row.insert(2,self.munici[row[0][:5]])
                ic.insertRow(row)
        arcpy.AddJoin_management(altas,"CVE_LOCALI",renom,"CVE_LOC")
        arcpy.SelectLayerByAttribute_management(altas,"NEW_SELECTION",'"{0}.TABEQUIV" = 0'.format(renom.name))
        arcpy.RemoveJoin_management(altas)
        #arcpy.CalculateField_management(altas,"FCH_INICIO","time.strftime('{0}')".format(_utils.change_format(parameters[3])),"PYTHON")
        arcpy.CalculateField_management(altas,"FCH_INICIO","time.strftime('{0}')".format(change_format(fch)),"PYTHON")
        arcpy.SelectLayerByAttribute_management(altas,"SWITCH_SELECTION")
        arcpy.CalculateField_management(altas,"FCH_INICIO","time.strftime('{0}')".format(change_format(fch)),"PYTHON")
        del altas
        self.flm.removeAll()
        self.flm.loadFromString(u'CVE_LOCALI "CVE_LOCALI" true true false 10 Text 0 0 ,First,#,{0},CVE_LOC,-1,-1'.format(bajas.name))
        arcpy.TableToTable_conversion(bajas,arcpy.env.workspace,"a_loc_baja_{0}.dbf".format(tab.name[-5:]),None,self.flm)
        arcpy.mapping.RemoveTableView(self.mxd.activeDataFrame,bajas)
        bajas = arcpy.mapping.TableView("a_loc_baja_{0}.dbf".format(tab.name[-5:]))
        arcpy.AddField_management(bajas,*(u'FCH_FINAL', u"DATE"))
        arcpy.AddJoin_management(bajas,"CVE_LOCALI",renom,"CVE_LOC")
        arcpy.SelectLayerByAttribute_management(bajas,"NEW_SELECTION",'"{0}.TABEQUIV" = 0'.format(renom.name))
        arcpy.RemoveJoin_management(bajas)
        #arcpy.CalculateField_management(bajas,"FCH_FINAL","time.strftime('{0}')".format(_utils.change_format(parameters[3])),"PYTHON")
        arcpy.CalculateField_management(bajas,"FCH_FINAL","time.strftime('{0}')".format(change_format(fch)),"PYTHON")
        arcpy.SelectLayerByAttribute_management(bajas,"SWITCH_SELECTION")
        arcpy.CalculateField_management(bajas,"FCH_FINAL","time.strftime('{0}')".format(change_format(fch)),"PYTHON")
        del bajas
        return
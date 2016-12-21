# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function, absolute_import
from arcpy.mapping import MapDocument, ListLayers, ListTableViews, TableView, RemoveTableView, AddTableView
from arcpy import env, Parameter, AddJoin_management, FieldMappings, TableToTable_conversion, RemoveJoin_management, AddField_management
from arcpy import Merge_management, SelectLayerByAttribute_management, CalculateField_management
from shutil import copy
from time import localtime as LT
import os
from .utils import download, matching

class cat_loc(object):
    def __init__(self):
        self.__licens = "users"
        env.overwriteOutput = True

    @property
    def _license(self):
        return True

    @property
    def params(self):
        param0 = Parameter('input_cat','Catalogo CENFEMUL',"Input",'GPFeatureLayer','Required')
        param1 = Parameter('input_loc','CAT_LOC mes anterior',"Input",'GPTableView','Required')
        return [param0,param1]

    def execute(self, parameters, messages):
        mxd = MapDocument('current')
        lyr = ListLayers(mxd,parameters[0].valueAsText,mxd.activeDataFrame)[0]
        loc = ListTableViews(mxd,parameters[1].valueAsText,mxd.activeDataFrame)[0]
        os.chdir(lyr.workspacePath)
        os.chdir('..')
        day={0:"LUNES",1:"MARTES",2:"MIERCOLES",3:"JUEVES",4:"VIERNES",5:"SABADO",6:"DOMINGO"}
        mon=["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]
        def mkd(fol,cd = True):
            if not os.path.isdir(fol):
                os.mkdir(fol)
            if cd:
                os.chdir(fol)
        mkd(u'{0}\\PROCESO_EQUIVALENCIAS_{1}'.format(os.getcwd(),"".join(map(lambda x: "0{0}".format(x) if x<10 else str(x),LT()[:3]))))
        mkd(u'{0}\\CATALOGO_{1}_{2}'.format(os.getcwd(),"".join(m for m in mon if lyr.name[-5:-2] in m),lyr.name[-2:]))
        mkd(u'{0}\\01-ESTANDARIZADAS-VICKY-{1}'.format(os.getcwd(),"".join(map(lambda x: "0{0}".format(x) if x<10 else str(x),LT()[:3]))+day[LT().tm_wday][:2]),False)
        mkd(u'{0}\\02-RESPALDO_ARCSDE_{1} - {2}'.format(os.getcwd(),lyr.name[-5:],"".join(map(lambda x: "0{0}".format(x) if x<10 else str(x),LT()[:3]))+day[LT().tm_wday][:2]),False)
        mkd(u'{0}\\03-CAPAS Y TABLAS FINALES'.format(os.getcwd()))
        mkd(u'{0}\\CAT_LOC'.format(os.getcwd()))
        #copy(loc.dataSource,u'{0}\\cat_loc_{1}.dbf'.format(os.getcwd(),lyr.name[-5:].lower()))
        AddJoin_management(lyr,"CVE_LOCC",loc,"CVE_LOCC")
        flm = FieldMappings()
        flm.loadFromString(u'CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},{0}.CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},{0}.CVE_LOCC,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},{0}.NOM_LOC,-1,-1;TIPO "TIPO" true true false 1 Text 0 0 ,First,#,{0},{0}.AMBITO,-1,-1'.format(lyr.name))
        TableToTable_conversion(lyr,os.getcwd(),"locs_faltantes.dbf","\"{0}.CVE_LOCC\" IS NULL".format(loc.name),flm)
        flm.removeAll()
        lfs = TableView(u"{0}\\locs_faltantes.dbf".format(os.getcwd()))
        RemoveJoin_management(lyr)
        for fld_ops in [[u'NOM_LOCORI', u'TEXT', 0, 0, 120], [u'CIGEL05', u'SHORT', 4, 0, 4], [u'ITER05', u'SHORT', 4, 0, 4], [u'CATVIG', u'SHORT', 4, 0, 4], [u'ITER10', u'SHORT', 4, 0, 4]]:
            AddField_management(lfs,*fld_ops)
        CalculateField_management(lfs,"CATVIG","1","PYTHON")
        Merge_management([loc,lfs],u'{0}\\cat_loc_{1}.dbf'.format(os.getcwd(),lyr.name[-5:].lower()))
        RemoveTableView(mxd.activeDataFrame,loc)
        loc = TableView(u'{0}\\cat_loc_{1}.dbf'.format(os.getcwd(),lyr.name[-5:].lower()))
        AddJoin_management(loc,"CVE_LOCC",lyr,"CVE_LOCC")
        CalculateField_management(loc,u"{0}.CATVIG".format(loc.name),u"isvig(!{0}.CVE_LOCC!)".format(lyr.name),"PYTHON","def isvig(fld):\n    if fld == None:\n        return 0\n    else:\n        return 1")
        SelectLayerByAttribute_management(loc,"NEW_SELECTION",u"\"{0}.CATVIG\" = 1 AND \"{0}.NOM_LOC\" <> \"{1}.NOM_LOC\"".format(loc.name,lyr.name))
        CalculateField_management(loc,u"{0}.NOM_LOCORI".format(loc.name),u"!{0}.NOM_LOC!".format(loc.name),"PYTHON")
        CalculateField_management(loc,u"{0}.NOM_LOC".format(loc.name),u"!{0}.NOM_LOC!".format(lyr.name),"PYTHON")
        SelectLayerByAttribute_management(loc,"CLEAR_SELECTION")
        RemoveJoin_management(loc)
        del lfs
        for lfs in os.listdir(os.getcwd()):
            if "locs_faltantes" in lfs and lfs.split('.')[-1] != "lock":
                os.remove(u"{0}\\{1}".format(os.getcwd(),lfs))
        LEEME = open(u"{0}\\LEEME.txt".format(os.getcwd()),'w')
        LEEME.write(u'1) Cotejar que el campo Nom_loc en la tabla CAT_LOC tenga de ancho menor a 120.\n\n2) Si tomamos la opci\xf3n 2 para subir el catalogo de localidades por STAT_TRANSFER\n   se debe tener una conexi\xf3n a la base de datos en Oracle con el usuario CARTO2010.\n\n3) Se deber\xe1 correr el script ubicado en CAT_LOC/OPCION02-STAT-TRANSFER\n\n4) En el cat_loc se deber\xe1n mantener todos las localidades aunque no pertenezcan a \n   ning\xfan cat\xe1logo ITER05, CIGEL05, ITER10 y CATVIG.\n\n'.encode("utf-8"))
        LEEME.close()
        mkd(u'{0}\\OPCION02-STAT-TRANSFER'.format(os.getcwd()))
        LEEME = open(u"{0}\\SCRIPT-SQL_{1}.txt".format(os.getcwd(),lyr.name[-5:]),'w')
        LEEME.write(u'--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\nDROP TABLE CAT_LOC CASCADE CONSTRAINTS ; \n\n--CREATE TABLE CAT_LOC ( \n  CVE_MUNC     VARCHAR2 (5), \n  CVE_LOCC     VARCHAR2 (9), \n  NOM_LOC      VARCHAR2 (120), \n  TIPO         VARCHAR2 (1),\n  NOM_LOCORI   VARCHAR2 (120),\n  CIGEL05      NUMBER (4),\n  ITER05       NUMBER (4), \n  CATVIG       NUMBER (4), \n  ITER10       NUMBER (4)); \n\n\n--CREATE UNIQUE INDEX IDX_CVELOCC_TCL ON "CARTO2010".CAT_LOC(CVE_LOCC); \n\n--CREATE INDEX IDX_CVEMUNC_TCL ON "CARTO2010".CAT_LOC(CVE_MUNC); \n\n\n--GRANT SELECT ON "CARTO2010"."CAT_LOC" TO "SISWEB2011P_OWNER";\n\n\n\n--================ PARA ALTERAR LA ESTRUCTURA DE LA TABLA ========\n--ALTER TABLE CARTO2010.CAT_LOC ADD CIGEL05 NUMBER(4);\n--ALTER TABLE CARTO2010.CAT_LOC ADD ITER10 NUMBER(4);\n\n\n--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n\n\n-- PASOS PARA SUBIR CATALOGO DE LOCALIDADES (CAT_LOC)\n\n\nPASO #01: SUBIR TABLA DBF YA SEA IMPORTANDOLA DESDE ARCCATALOG O AL ORACLE CON STAT-TRANSFER,\n          UTILIZANDO EL USUARIO CARTO2010.\n\t  \n\t  LA TABLA SE DENOMINARA "TMP_CAT_LOC_{0}"\n\nPASO #02: EJECUTAR EL SIGUIENTE SCRIPT EN SQLDEVELOPER.\n\n\nSELECT * FROM TMP_CAT_LOC_{0};\n\nSELECT * FROM TMP_CAT_LOC_{0} WHERE NOM_LOC LIKE \'%\xd1%\'; \n\nSELECT LENGTH(NOM_LOC) FROM TMP_CAT_LOC_{0} ORDER BY 1 DESC;\n\nSELECT NOM_LOCORI,LENGTH(TRIM(NOM_LOCORI)) FROM TMP_CAT_LOC_{0} ORDER BY 1 DESC;\n\nSELECT NOM_LOCORI,LENGTH(TRIM(NOM_LOCORI)) FROM TMP_CAT_LOC_{0} WHERE NOT NOM_LOCORI IS NULL ORDER BY LENGTH(TRIM(NOM_LOCORI)) DESC;\n\nSELECT * FROM TMP_CAT_LOC_{0} WHERE CVE_LOC=\'010010001\';\n\n\n-- ALTER TABLE CARTO2010.CAT_LOC MODIFY NOM_LOC VARCHAR2(120);\n-- ALTER TABLE CARTO2010.CAT_LOC MODIFY NOM_LOCORI VARCHAR2(120);\n\nTRUNCATE TABLE CAT_LOC;\n\n--319,178 LOCALIDADES (CIGEL,ITER,CENFEMUL)\nINSERT INTO CAT_LOC (SELECT TRIM(CVE_MUNC) AS CVE_MUNC,TRIM(CVE_LOCC) AS CVE_LOCC, TRIM(NOM_LOC)AS NOM_LOC, TIPO, TRIM(NOM_LOCORI) AS NOM_LOCORI, CIGEL05, ITER05, CATVIG, ITER10 FROM TMP_CAT_LOC_{0});\n\nCOMMIT;\n\nSELECT * FROM CAT_LOC;\n\nSELECT * FROM CAT_LOC WHERE NOM_LOC LIKE \'TING%\';\n\nDROP TABLE TMP_CAT_LOC_{0};\n\nCOMMIT;\n'.format(lyr.name[-5:]).encode("utf-8"))
        LEEME.close()
        os.chdir('..')
        os.chdir('..')

        for fol in ("CAT_MUN","N_LOCVIGENTE","T_ACTVIGENTE","T_COORD_ACTVIGENTE","T_COORD_EQUIVAL","T_COORD_INVTERR","T_EQUIVALENCIAS"):
            mkd(u'{0}\\{1}'.format(os.getcwd(),fol),False)

        coords = os.path.join(os.path.dirname(lyr.workspacePath),"PROCESO_COORDENADAS","FINAL")

        Merge_management(lyr,u"{0}\\{1}.shp".format(os.path.join(os.getcwd(),"N_LOCVIGENTE"),lyr.name.replace("_CENFEMUL","")))

        for doc in os.listdir(lyr.workspacePath):
            if matching("REGISTRO_DE_ACTUALIZACION_.*[.]dbf$",doc):
                copy(u"{0}\\{1}".format(lyr.workspacePath,doc),os.path.join(os.getcwd(),"T_ACTVIGENTE"))
                #tab = TableView(os.path.join(lyr.workspacePath,doc))
                #AddTableView(mxd.activeDataFrame,tab)
                #tab = ListTableViews(mxd,tab.name,mxd.activeDataFrame)[0]
                #flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},CVE_MUNC,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;NOM_ENT "NOM_ENT" true true false 110 Text 0 0 ,First,#,{0},NOM_ENT,-1,-1;NOM_ABR "NOM_ABR" true true false 32 Text 0 0 ,First,#,{0},ABR_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 110 Text 0 0 ,First,#,{0},NOM_LOC,-1,-1;DESCGO_ACT "DESCGO_ACT" true true false 80 Text 0 0 ,First,#,{0},DESCGO_ACT,-1,-1;CGO_ACT "CGO_ACT" true true false 2 Text 0 0 ,First,#,{0},CGO_ACT,-1,-1;AMBITO "AMBITO" true true false 1 Text 0 0 ,First,#,{0},AMBITO,-1,-1;FECHA_ACT "FECHA_ACT" true true false 10 Text 0 0 ,First,#,{0},FECHA_ACT,-1,-1'.format(tab.name))
                #TableToTable_conversion(tab,os.path.join(os.getcwd(),"T_ACTVIGENTE"),doc,None,flm)
                #flm.removeAll()
            elif matching("TABLA_DE_EQUIVALENCIA_.*[.]dbf$",doc):
                copy(u"{0}\\{1}".format(lyr.workspacePath,doc),os.path.join(os.getcwd(),"T_EQUIVALENCIAS"))

        for doc in os.listdir(coords):
            if matching("t_coord_actvigente_.*[.]dbf$",doc):
                tab = TableView(os.path.join(coords,doc))
                AddTableView(mxd.activeDataFrame,tab)
                tab = ListTableViews(mxd,tab.name,mxd.activeDataFrame)[0]
                flm.loadFromString(u'LNG_DG "LNG_DG" true true false 14 Double 8 13 ,First,#,{0},LNG_DG,-1,-1;LAT_DG "LAT_DG" true true false 12 Double 8 11 ,First,#,{0},LAT_DG,-1,-1;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1'.format(tab.name))
                Merge_management(tab,os.path.join(os.getcwd(),*("T_COORD_ACTVIGENTE",doc)))
                copy(u"{0}\\{1}".format(coords,doc),os.path.join(os.getcwd(),*("T_COORD_INVTERR","t_coord_invterr10.dbf")))
            elif matching("t_coord_equival_.*[.]dbf$",doc):
                copy(u"{0}\\{1}".format(coords,doc),os.path.join(os.getcwd(),"T_COORD_EQUIVAL"))
        os.chdir("..")

        deposit_path = os.path.dirname(os.path.abspath(__file__))
        copy(os.path.join(deposit_path,'tables','01-Structuras_Catalogos.xlsx'),'01-Structuras_Catalogos.xlsx')
        #download('https://raw.githubusercontent.com/dgaae/data/master/tables/01-Structuras_Catalogos.xlsx',os.path.join(os.getcwd(),"01-Structuras_Catalogos.xlsx"))
        with open(os.path.join(os.getcwd(),"00-Informacion.txt"),'w') as op:
            op.write(u'\n"Catalogo_{0}.shp"                 ES IGUAL A "N_LOCVIGENTE"\n\n\n"Registro_Actualizacion_{0}.dbf"   ES IGUAL A "T_ACTVIGENTE"\n\n\n"Tab_Equivalencias_{0}.dbf"        ES IGUAL A "T_EQUIVALENCIAS"\n\n\n"CatLocalidades_{0}.dbf"           ES IGUAL A "T_COORD_ACTVIGENTE"\n\n\n"Tab_Equivalencias_{0}_Coord.dbf"  ES IGUAL A "T_COORD_EQUIVAL"\n\n\n\n\n'.format(lyr.name[-5:-2]+str(int(lyr.name[-2:])+2000)).encode('cp1254'))

        with open(os.path.join(os.getcwd(),"PASO01-ELIMINAR INFORMACION.txt"),'w') as op:
            op.write(u'--===================================================================================\n--*************************** I M P O R T A N T E ***********************************\n--===================================================================================\n\nANTES DE EMPEZAR CON EL PROCESO DE ACTUALIZACION SE DEBER\xc1 DAR DE BAJA LOS SERVICIOS\nDE LA PAGINA UBICADO EN 172.25.38.138\n\n--===================================================================================\n\n\nNOTA: ANTES DE HACER CUALQUIER COSA, REVISAR INDICES DE CAPAS Y TABLAS.\n\nELIMINAR LA SIGUIENTE INFORMACION EN CASO DE CONTAR CON ALGUNA ACTUALIZACION\n\n\n\nELIMINAR LA SIGUIENTE CAPA\n\n1) N_LOCVIGENTE2010\n\n\n\nELIMINAR LAS SIGUIENTES TABLAS\n\n1) T_ACTVIGENTE\n\n2) T_EQUIVALENCIAS\n\n3) T_COORD_ACTVIGENTE  (SOLO SI EXISTE UNA NUEVA VERSION)\n\n4) T_COORD_EQUIVAL     (SOLO SI EXISTE UNA NUEVA VERSION)\n\n\n\n\n\n\n\n\n\n\n'.encode('cp1254'))

        with open(os.path.join(os.getcwd(),"PASO02-CARGAR INFORMACION.txt"),'w') as op:
            op.write(u'\nCARGAR LA SIGUIENTE CAPA\n\n1) N_LOCVIGENTE2010\n\n\n\nCARGAR LAS SIGUIENTES TABLAS\n\n1) CAT_LOC (CATALOGO DE LOCALIDADES: SEGUIR PASOS EN "\\03-CAPAS Y TABLAS FINALES\\CAT_LOC\\SCRIPT")\n\n2) T_ACTVIGENTE\n\n3) T_EQUIVALENCIAS\n\n4) T_COORD_ACTVIGENTE  (SOLO SI EXISTE UNA NUEVA VERSION)\n\n5) T_COORD_EQUIVAL     (SOLO SI EXISTE UNA NUEVA VERSION)\n\n\n\n-- ::::::::::::::::::::::::::::::::::::::::::::\n-- :: NOTA: GENERAR INDICES A CAPAS Y TABLAS ::\n-- ::::::::::::::::::::::::::::::::::::::::::::\n\n1) CAT_LOC\n\nIDX_CVELOC_TCL (CVE_LOCC, UNIQUE, ASCENDING)\nIDX_CVEMUN_TCL (CVE_MUNC, ASCENDING)\n\n2) N_LOCVIGENTE2010\n\nIDX_CVELOC_LVIG (CVE_LOCC, UNIQUE, ASCENDING)\nIDX_CVEM_LVIG (CVE_MUNC, ASCENDING)\n\n\n3) T_ACTVIGENTE\n\nIDX_ACTVIGENTE (CVE_LOCC, ASCENDING)\n\n\n4) T_EQUIVALENCIAS\n\nIDX_EQUIV_LOCACT (CVELOCCACT, ASCENDING)\n\nIDX_EQUIV_LOCORI (CVELOCCORI, ASCENDING)\n\n\n5) T_COORD_ACTVIGENTE\n\nIDX_COORD_ACTVIG (CVE_LOCC, UNIQUE, ASCENDING)\n\n\n6) T_COORD_EQUIVAL\n\nIDX_COORD_EQUIV (CVELOCCACT, ASCENDING)\n\n \n\n\n\n\n'.encode('cp1254'))

        with open(os.path.join(os.getcwd(),"PASO03-ASIGNAR PRIVILEGIOS.txt"),'w') as op:
            op.write(u'-- *******************************************************************************\n-- ASIGNAR PRIVILEGIOS A CAPAS Y TABLAS DE INFORMACION\n-- *******************************************************************************\n\nSELECT TABLE_NAME, \'S\'||LAYER_ID AS "S",\'F\'||LAYER_ID AS "F"\nFROM SDE.LAYERS WHERE OWNER=\'"CARTO2010"\'AND TABLE_NAME LIKE UPPER(\'%NOMCAPA%\')\nORDER BY TABLE_NAME;\n\n\nGRANT SELECT ON "CARTO2010"."CAT_LOC" TO "SISWEB2011P_OWNER";\n\nGRANT SELECT ON "CARTO2010"."T_COORD_ACTVIGENTE" TO "SISWEB2011P_OWNER";\nGRANT SELECT ON "CARTO2010"."T_COORD_EQUIVAL" TO "SISWEB2011P_OWNER";\n\nGRANT SELECT ON "CARTO2010"."N_LOCVIGENTE2010" TO "SISWEB2011P_OWNER";\n\nGRANT SELECT ON "CARTO2010"."T_ACTVIGENTE" TO "SISWEB2011P_OWNER";\nGRANT SELECT ON "CARTO2010"."T_EQUIVALENCIAS" TO "SISWEB2011P_OWNER";\n\n\nCOMMIT;\n\n\n**********************************************\n\nSISWEB2011P_SELECT (SELECT): N_LOCVIGENTE (CARTOGRAFIA2010)\n\n\nTODAS LAS VN TAMBIEN CORRER EL PRIVILEGIO: SISWEB2011P_SELECT, SELECT'.encode('cp1254'))

        with open(os.path.join(os.getcwd(),"PASO04-RECOMPILAR VISTAS.txt"),'w') as op:
            op.write(u'REVISAR LAS VISTAS POR SI ALGUNA VISTA SE TRONO \n\nVOLVER A COMPILAR LAS SIGUIENTES VISTAS EN CASO DE QUE MARQUE UN ERROR (CRUZ DE COLOR ROJO EN EL ENTORNO DE SQL DEVELOPER)\n\nLAS SIGUIENTES SON CAPAS QUE DEPENDEN DE CAT_LOC\n\n1) VT_PRESPROGLOC2010\n\n2) VT_LECHERIA2010\n\n3) VT_DICONSAT2010\n\n4) VT_DICONSAA2010\n\n\n'.encode('cp1254'))

        with open(os.path.join(os.getcwd(),"PASO05-ANALISIS DE EQUIVALENCIAS.txt"),'w') as op:
            op.write(u'--::::::::::::: EQUIVALENCIAS ITER 2010 VS CENFEMUL ::::::::::::::\n\n1) SEGUIR EL PROCEDIMIENTO DE LOS SCRIPTS LOCALIZADOS EN LA SIGUIENTE CARPETA\n\n"\\Analisis con Cat_EquivMAR - 20160421JU\\"\n\n\n\n'.encode('cp1254'))

        return
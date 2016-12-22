


# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function
from arcpy import Parameter, mapping, RefreshTOC, SetProgressor, CreateUniqueName, AddMessage, SetProgressorPosition, Statistics_analysis, ResetProgressor, ListFields, AddField_management, AddJoin_management, CalculateField_management, RemoveJoin_management, FieldMappings, SetProgressorLabel, DeleteField_management, TableToTable_conversion, SelectLayerByAttribute_management,Merge_management
from arcpy.da import SearchCursor,InsertCursor, UpdateCursor
from os.path import join
from os import mkdir, chdir, listdir, walk, getcwd, remove
from datetime import datetime
from shutil import copy2
from .utils import mktable,mklistdir
from .equivalencias import calc_equiv
from .data import bar


__all__ = ["disp_movil"]

class disp_movil(calc_equiv):
    def __init__(self):
        self.__licens = "users"
        self.path = bar.fpath

    @property
    def _license(self):
    	return True
        #return utils.license_v2(utils.licens.lists[self.__licens])

    @property
    def params_recarch(self):
        pm0 = Parameter('savedir','Ruta de salida:','Input','DEWorkspace','Required')
        pm1 = Parameter('befdir',u'Catálogo anterior:'.encode('cp1254'),'Input','DEWorkspace','Required')
        pm2 = Parameter('locsiter10vscenfemul','Archivo "locsiter10vscenfemul.dbf":','Input','DETable','Required')
        pm3 = Parameter('c_munici',u'Archivo "C_MUNICI.dbf" (Sólo si fue modificado):'.encode("cp1254"),'Input','DETable','Optional')
        pm4 = Parameter('input_cat',u'Cat\xe1logos disponibles',"Input",'String','Required')
        params = [pm0,pm1,pm2,pm3,pm4]
        return params
    
    @property
    def params_process(self):
        pm0 = Parameter('cat_localidad','Catalogo de localidades:','Input','GPTableView','Optional')
        pm1 = Parameter('cat_agebs',u'Catálogo de AGEBS:'.encode("cp1254"),'Input','GPTableView','Optional')
        pm2 = Parameter('cat_manzanas',u'Catálogo de manzanas:'.encode("cp1254"),'Input','GPTableView','Optional')
        pm3 = Parameter('cat_cp',u'Catálogo de codigos postales:'.encode("cp1254"),'Input','GPTableView','Optional')
        pm4 = Parameter('cat_asentamientos',u'Catálogo de asentamientos:'.encode("cp1254"),'Input','GPTableView','Optional')
        pm5 = Parameter('cat_vialidades',u'Catálogo de vialidades:'.encode("cp1254"),'Input','GPTableView','Optional')
        pm6 = Parameter('main_path','Carpeta que contiene los archivos para el procesamiento (Corrida Scripts):','Input','DEWorkspace','Required')
        params = [pm0,pm1,pm2,pm3,pm4,pm5,pm6]
        return params

    def mapping_tab(self,tabla):
        mxd = mapping.MapDocument("CURRENT")
        df = mapping.ListDataFrames(mxd, "*")[0]
        mapping.AddTableView(df,tabla)
        RefreshTOC()
        return

    def makindir(self,parameters):
        #-----------Variables X el usuario-----------
        main_path = parameters[0].valueAsText
        bef_path = parameters[1].valueAsText
        SetProgressor("Step","Iniciando..",0,9,1)
        bef_dir = join(bef_path,'DISPOSITIVOS_MOVILES')
        fch = main_path.split('\\')[-1].split('_')[-2:]
        fech_act = datetime.strptime('{0}{1}'.format(fch[0],fch[1]),'%B%Y')
        fch = bef_path.split('\\')[-1].split('_')[-2:]
        fech_ant = datetime.strptime('{0}{1}'.format(fch[0],fch[1]),'%B%Y')
        del fch
        SetProgressorPosition(1)
        #____________________________________________
        #------------Creando directorio------------
        SetProgressorLabel(u"Recolectando directorios..")
        main_dir = CreateUniqueName(join(main_path,'DISPOSITIVOS_MOVILES'))
        mkdir(main_dir)
        AddMessage(u"Se creó: {0}".format(main_dir).encode('cp1254'))
        chdir(main_dir)
        dirs = ['01 - TABLAS BASE A UTILIZAR','02 - TABLAS BASE ACTUALIZAR CADA MES','03 - CATALOGOS_BASE','04 - CORRIDA_SCRIPTS_DISPOSITIVOS_MOVILES_{0}'.format(fech_act.strftime('%b%y').replace('.','').upper()),'05 - CORRIDA_SCRIPT_SEPARADA_POR_ENTIDAD','06 - FINALES_ID_SIIPSO','07 - SCRIPTS','08 - ENTREGAR_A_RUBEN']
        mklistdir(dirs)
        #__________________________________________
        #--------Copiando archivos necesarios--------
        SetProgressorLabel(u"Recopilando archivos necesarios..")
        chdir(dirs[0])
        copy_dir = join(bef_dir,dirs[0])
        for fil in [u'ageb_urb.dbf',u'irs2010_por_municipio.dbf',u'C_MUNICI.dbf']:
            copy2(join(copy_dir,fil),fil)
        if parameters[3].altered:
            copy2(parameters[3].valueAsText,u'C_MUNICI.dbf')
        SetProgressorPosition(2)
        chdir(join(main_dir,dirs[1]))
        copy2(join(main_path,'PROCESO_SIIPSO','CATALOGO_EMBONADO_CON_CAT_{0}\\LOC_ACT_{0}.DBF'.format(fech_act.strftime('%b%y').replace('.','').upper())),'LOC_ACT.DBF')
        copy_dir = join(bef_dir,dirs[1])
        SetProgressorPosition(3)
        
        copy2(join(copy_dir,'equiv_vial_vs_cenfemul_{0}.dbf'.format(fech_ant.strftime('%b%y').replace('.',''))),'equiv_vial_vs_cenfemul_{0}.dbf'.format(fech_act.strftime('%b%y').replace('.','')))
        #copy2(parameters[2].valueAsText,'locsiter10vscenfemul{0}.dbf'.format(fech_act.strftime('%b%y')))
        chdir(join(main_dir,dirs[2]))
        copy_dir = join(bef_dir,dirs[2])
        SetProgressorPosition(4)
        for fil in ['cat_agebs.dbf','cat_manzanas.dbf','cat_municipio.dbf','cat_vialidades_completo.dbf']:
            copy2(join(copy_dir,fil),fil)
        copy2(join(main_path,'CATALOGO_A_ENTREGAR','CATALOGO_CENFEMUL_{0}.dbf'.format(fech_act.strftime('%b%y').replace('.',''))),'cat_localidad.dbf')
        embo = listdir(join(main_path,'CATALOGO_SEPOMEX'))[10]
        SetProgressorPosition(5)
        copy2(join(main_path,'CATALOGO_SEPOMEX',embo,'C_ASENTA.dbf'),'cat_asentamientos.dbf')
        copy2(join(main_path,'CATALOGO_SEPOMEX',embo,'C_CODIGO.dbf'),'cat_cp.dbf')
        del copy_dir, fil
        #____________________________________________
        #------Pasando todo a CORRIDA_SCRIPTS_DISPOSITIVOS_MOVILES------
        SetProgressorPosition(6)
        SetProgressorLabel(u"Pasando todo a la carpeta 'CORRIDA SCRIPTS DISPOSITIVOS MOVILES'..")
        chdir(main_dir)
        for root,dires,files in walk(".", topdown=False):
            if not dirs[3] in root:
                for name in files:
                    if name.endswith('_{0}.dbf'.format(fech_act.strftime('%b%y').replace('.',''))):
                        fil = name.replace('_'+fech_act.strftime('%b%y').replace('.',''),'')
                    elif name.endswith('{0}.dbf'.format(fech_act.strftime('%b%y').replace('.',''))):
                        fil = name.replace(fech_act.strftime('%b%y').replace('.',''),'')
                    else:
                        fil = name
                    copy2(join(main_dir,root.split('\\')[1],name),join(main_dir,dirs[3],fil))
        chdir(join(main_dir,dirs[3]))
        SetProgressorPosition(7)
        SetProgressorLabel(u"Creando agregado del catálogo de municipios".encode('cp1254'))
        Statistics_analysis('C_MUNICI.dbf',join(getcwd(),'Sumarize_c_municipi.dbf'),[["C_MUN","MAX"]],"CVE_MUN")
        SetProgressorPosition(8)
        ResetProgressor()
        del fil
        #_______________________________________________________________
        #---------directorio en CORRIDA_SCRIPTS_DISPOSITIVOS_MOVILES------
        chdir(join(main_dir,dirs[7]))
        mklistdir([u'FINAL',U'PROCESO'])
        chdir(u'FINAL')
        mkdir(u'BAJAS_ALTAS_AGEBS_MZAS')
        chdir(join(main_dir,dirs[3]))
        mklistdir([u'FINALES',u'FINALES_ID_SIIPSO',u'MODIFICAR_CAT_AGEBS_Y_MZAS_EN_CLAVES',u'RESPALDO'])
        SetProgressorPosition(9)
        ResetProgressor()
        return

    def map_all(self):
        for tabla in [u'cat_localidad.dbf',u'cat_agebs.dbf',u'cat_manzanas.dbf',u'cat_cp.dbf',u'cat_asentamientos.dbf',u'cat_vialidades_completo.dbf']:
            disp_movil.mapping_tab(self,mapping.TableView(tabla))
        return

    def set_sum(self,parameters):
        Statistics_analysis('cat_agebs.dbf',join(getcwd(),'Sumarize_agebs.dbf'),[["CVE_LOCC","COUNT"]],"CVE_LOCC")
        tab_sum = mapping.TableView('Sumarize_agebs.dbf')
        fields = [[u"CVE_LOC","TEXT",0,0,9],[u"CVE_ACT","TEXT",0,0,9]]
        for fld in fields:
            AddField_management(tab_sum,*fld)
        tab_iter = mapping.TableView(parameters[2].valueAsText)
        AddJoin_management(tab_sum,"CVE_LOCC",tab_iter,"CVE_ITER10","KEEP_ALL")
        sel = SelectLayerByAttribute_management(tab_sum,"NEW_SELECTION",""""CVE_ITER10" is Null""")
        CalculateField_management(tab_sum,"Sumarize_agebs.CVE_LOC","!Sumarize_agebs.CVE_LOCC!","PYTHON")
        RemoveJoin_management(tab_sum)
        return tab_sum

    def locsiter(self,parameters,cvs):
        tab_iter = mapping.TableView(parameters[2].valueAsText)
        flm = FieldMappings()
        flm.loadFromString(u'CVE_ITER10 "CVE_ITERa10" true true false 9 Text 0 0 ,First,#,{0},{1}.CVE_LOC,-1,-1;CVECEFEMUL "CVECEFEMUL" true true false 9 Text 0 0 ,First,#,{0},{1}.CVE_ACT,-1,-1'.format(tab_iter.name,cvs.name))
        Merge_management([tab_iter,cvs],join(getcwd(),"locsiter10vscenfemul.dbf"),flm)
        tab_locs = mapping.TableView("locsiter10vscenfemul.dbf")
        expr = """def calc(it,loc):
            if it == ' ':
                return loc
            else:
                return it"""
        CalculateField_management(tab_locs,"CVE_ITER10","calc(!CVE_ITER10!,!CVE_LOC!)","PYTHON",expr)
        CalculateField_management(tab_locs,"CVECEFEMUL","calc(!CVECEFEMUL!,!CVE_ACT!)","PYTHON",expr)
        for fld in ListFields('locsiter10vscenfemul.dbf'):
            if fld.name not in [u'CVE_ITER10', u'CVECEFEMUL',u'OID']:
                DeleteField_management(tab_locs,fld.name)
        return

    def localidad(self,parameters):
        SetProgressor("Step",u"Proceso para localidades:\nIniciando..",0,13,1)
        SetProgressorPosition(1)
        chdir(parameters[6].valueAsText)
        mxd = mapping.MapDocument("CURRENT")
        tab_loc = mapping.ListTableViews(mxd,'cat_localidad')[0]
        disp_movil.cat_localidad(self,tab_loc)
        SetProgressorLabel(u"Proceso para localidades:\nCreando cat_localidad_completo.dbf..")
        flds = [fld.name for fld in ListFields(tab_loc.name)]
        SetProgressorPosition(10)
        copy2('{0}.dbf'.format(join(tab_loc.workspacePath,tab_loc.name)),'cat_localidad_completo.dbf')
        tab_loc = mapping.TableView('cat_localidad_completo.dbf')
        with SearchCursor(tab_loc,flds) as sc:
            rows = [row for row in sc]
        if u'FINALES' not in listdir(getcwd()):
            mkdir('FINALES')
        chdir('FINALES')
        SetProgressorPosition(11)
        SetProgressorLabel(u"Proceso para localidades:\nCreando catálogo de localidades final..".encode('cp1254'))
        fields = [[u'ID_LOC', u'DOUBLE', 13, 0, 14],[u'ENTIDAD_ID', u'DOUBLE', 2, 0, 0],[u'MUN_ID', u'DOUBLE', 5, 0, 0],[u'CVE_LOCNUM', u'DOUBLE', 4, 0, 0],[u'NOM_LOC', u'TEXT', 0, 0, 110],[u'CVE_LOCSTR', u'TEXT', 0, 0, 4],[u'ESTRATO', u'DOUBLE', 1, 0, 0],[u'IRS', u'DOUBLE', 8, 4, 9],[u'AGEB_URB', u'DOUBLE', 1, 0, 0],[u'SITUA_LOC', u'DOUBLE', 1, 0, 0],[u'AMBITO', u'TEXT', 0, 0, 1]]
        tab_locf = mktable('cat_localidad.dbf',fields)
        SetProgressorPosition(12)
        with InsertCursor(tab_locf,[fld[0] for fld in fields]) as ic:
            for row in rows:
                ic.insertRow((row[20],row[21],row[22],row[23],row[7],row[24],row[25],row[26],row[27],row[28],row[8]))
            SetProgressorPosition(13)
        disp_movil.mapping_tab(self,tab_locf)
        ResetProgressor()
        del flds, tab_locf, tab_loc, fields, ic, row
        return

    def cat_localidad(self,tab_loc):
        fields = [[u'ID_LOC', u'DOUBLE', 13, 0, 14],[u'ENTIDAD_ID', u'DOUBLE', 2, 0, 0],[u'MUN_ID', u'DOUBLE', 5, 0, 0],[u'CVE_LOCNUM', u'DOUBLE', 4, 0, 0],[u'CVE_LOCSTR', u'TEXT', 0, 0, 4],[u'ESTRATO', u'DOUBLE', 1, 0, 0],[u'IRS', u'DOUBLE', 8, 4, 9],[u'AGEB_URB', u'DOUBLE', 1, 0, 0],[u'SITUA_LOC', u'DOUBLE', 1, 0, 0]]
        for fld in fields:
            AddField_management(tab_loc,*fld)
        SetProgressorPosition(2)
        tab_locact = mapping.TableView('LOC_ACT.dbf')
        SetProgressorLabel(u"Proceso para localidades:\nCalculando campos..")
        AddJoin_management(tab_loc,"CVE_LOCC",tab_locact,"CVE_LOC","KEEP_COMMON")
        CalculateField_management(tab_loc,"cat_localidad.ID_LOC","int(!LOC_ACT.C_LOC!)","PYTHON")
        SetProgressorPosition(3)
        del tab_locact
        RemoveJoin_management(tab_loc)
        CalculateField_management(tab_loc,"ENTIDAD_ID","int(!CVE_ENT!)","PYTHON")
        CalculateField_management(tab_loc,"CVE_LOCNUM","int(!CVE_LOCC![-4:])","PYTHON")
        SetProgressorPosition(4)
        CalculateField_management(tab_loc,"CVE_LOCSTR","!CVE_LOCC![-4:]","PYTHON")
        CalculateField_management(tab_loc,"SITUA_LOC","1","PYTHON")
        tab_sumcmun = mapping.TableView('Sumarize_c_municipi.dbf')
        SetProgressorPosition(5)
        AddJoin_management(tab_loc,"CVE_MUNC",tab_sumcmun,"CVE_MUN","KEEP_COMMON")
        CalculateField_management(tab_loc,"cat_localidad.MUN_ID","!Sumarize_c_municipi.MAX_C_MUN!","PYTHON")
        SetProgressorPosition(6)
        del tab_sumcmun
        RemoveJoin_management(tab_loc)
        codeblock = """def estrato(p_total):
            if p_total == 0:
                return 0
            if p_total >= 1 and p_total <=2499:
                return 4
            elif p_total >= 2500 and p_total <= 10000:
                return 3
            elif p_total >= 10001 and p_total <= 99999:
                return 2
            elif p_total >= 100000:
                return 1"""
        CalculateField_management(tab_loc,"ESTRATO","estrato(!P_TOTAL!)", "PYTHON_9.3",codeblock)
        SetProgressorPosition(7)
        tab_irs = mapping.TableView('irs2010_por_municipio.dbf')
        AddJoin_management(tab_loc,"CVE_MUNC",tab_irs,"CVE_MUNC","KEEP_COMMON")
        CalculateField_management(tab_loc,"cat_localidad.IRS","!irs2010_por_municipio.IRS2010!","PYTHON")
        SetProgressorPosition(8)
        RemoveJoin_management(tab_loc)
        del tab_irs
        tab_agburb = mapping.TableView('ageb_urb.dbf')
        AddJoin_management(tab_loc,"CVE_LOCC",tab_agburb,"CVE_LOCC","KEEP_COMMON")
        CalculateField_management(tab_loc,"cat_localidad.AGEB_URB","!ageb_urb.LOCURB!","PYTHON")
        SetProgressorPosition(9)
        RemoveJoin_management(tab_loc)
        del tab_agburb
        return

    def agebs(self,parameters):
        SetProgressor("Step","Proceso para AGEBS:\nIniciando..",0,10,1)
        SetProgressorPosition(1)
        chdir(parameters[6].valueAsText)
        dircor = ['FINALES','FINALES_ID_SIIPSO','MODIFICAR_CAT_AGEBS_Y_MZAS_EN_CLAVES','RESPALDO']
        disp_movil.cat_agebs(self)
        SetProgressorLabel(u"Proceso para AGEBS:\nCreando cat_agebs_completo.dbf..")
        copy2('cat_agebs.dbf','cat_agebs_completo.dbf')
        copy2('cat_agebs_completo.dbf',join(dircor[3],'cat_agebs_con_claves_dadas_de_baja.dbf'))
        SetProgressorPosition(7)
        tab_agbs = mapping.TableView(join(dircor[3],'cat_agebs_con_claves_dadas_de_baja.dbf'))
        DeleteField_management(tab_agbs,[fld.name for fld in ListFields('cat_agebs_completo.dbf')][1:8])
        SetProgressorPosition(8)
        copy2(join(dircor[3],'cat_agebs_con_claves_dadas_de_baja.dbf'),join(dircor[0],'cat_agebs.dbf'))
        tab_agbs = mapping.TableView(join(dircor[0],'cat_agebs.dbf'))
        SetProgressorLabel(u"Proceso para AGEBS:\nCreando catálogo de AGEBS final..".encode('cp1254'))
        SetProgressorPosition(9)
        with UpdateCursor(tab_agbs,"*") as uc:
            for row in uc:
                if row[1] == 0:
                    uc.deleteRow()
        SetProgressorPosition(10)
        disp_movil.mapping_tab(self,tab_agbs)
        ResetProgressor()
        del tab_agbs, dircor
        return

    def cat_agebs(self):
        fields = [[u'ID_LOC', u'DOUBLE', 13, 0, 14],[u'AGEB', u'TEXT', 0, 0, 13],[u'AGEB_ID', u'DOUBLE', 9, 0, 10],[u'MUN_ID', u'DOUBLE', 5, 0, 6],[u'ENTIDAD_ID', u'DOUBLE', 2, 0, 3]]
        mxd = mapping.MapDocument("CURRENT")
        tab_agb = mapping.ListTableViews(mxd,'cat_agebs')[0]
        for fld in fields:
            AddField_management(tab_agb,*fld)
        SetProgressorLabel(u"Proceso para AGEBS:\nCalculando campos..")
        SetProgressorPosition(2)
        tab_iter = mapping.TableView('locsiter10vscenfemul.dbf')
        AddJoin_management(tab_agb,"CVE_LOCC",tab_iter,"CVE_ITER10","KEEP_COMMON")
        SetProgressorPosition(3)
        tab_locact = mapping.TableView('LOC_ACT.dbf')
        AddJoin_management(tab_agb,"locsiter10vscenfemul.CVECEFEMUL",tab_locact,"CVE_LOC","KEEP_COMMON")
        SetProgressorPosition(4)
        CalculateField_management(tab_agb,"cat_agebs.ID_LOC","!LOC_ACT.C_LOC!","PYTHON")
        RemoveJoin_management(tab_agb)
        CalculateField_management(tab_agb,"AGEB","!CVE_AGEBC!","PYTHON")
        CalculateField_management(tab_agb,"AGEB_ID","!OID!+1","PYTHON")
        SetProgressorPosition(5)
        CalculateField_management(tab_agb,"ENTIDAD_ID","int(!CVE_ENT!)","PYTHON")
        tab_sumcmun = mapping.TableView('Sumarize_c_municipi.dbf')
        AddJoin_management(tab_agb,"CVE_MUNC",tab_sumcmun,"CVE_MUN","KEEP_COMMON")
        SetProgressorPosition(6)
        CalculateField_management(tab_agb,"cat_agebs.MUN_ID","!Sumarize_c_municipi.MAX_C_MUN!","PYTHON")
        RemoveJoin_management(tab_agb)
        return

    def manzanas(self,parameters):
        SetProgressor("Step","Proceso para manzanas:\nIniciando..",0,10,1)
        chdir(parameters[6].valueAsText)
        disp_movil.cat_manzanas(self)
        copy2('cat_manzanas_completo.dbf',join('RESPALDO','cat_manzanas_con_claves_dadas_de_baja.dbf'))
        SetProgressorLabel(u"Proceso para manzanas:\nCreando respaldo del catálogo de manzanas con claves dadas de baja..".encode('cp1254'))
        SetProgressorPosition(7)
        tab_mzs = mapping.TableView(join('RESPALDO','cat_manzanas_con_claves_dadas_de_baja.dbf'))
        DeleteField_management(tab_mzs,[u'CVE_ENT',u'CVE_MUNC',u'CVE_AGEBC',u'NOM_ENT',u'NOM_MUN',u'NOM_LOC'])
        SetProgressorLabel(u"Proceso para manzanas:\nProcesando archivo final de manzanas..")
        SetProgressorPosition(8)
        copy2(join('RESPALDO','cat_manzanas_con_claves_dadas_de_baja.dbf'),join('FINALES','cat_manzanas.dbf'))
        SetProgressorPosition(9)
        tab_mzs = mapping.TableView(join('FINALES','cat_manzanas.dbf'))
        with UpdateCursor(tab_mzs,"*") as uc:
            for row in uc:
                if row[8] == 'B':
                    uc.deleteRow()
        SetProgressorPosition(10)
        disp_movil.mapping_tab(self,tab_mzs)
        ResetProgressor()
        del tab_mzs, uc
        return

    def cat_manzanas(self):
        mxd = mapping.MapDocument("CURRENT")
        tab_mzs = mapping.ListTableViews(mxd,'cat_manzanas')[0]
        SetProgressorPosition(1)
        tab_agb = mapping.TableView(join('FINALES','cat_agebs.dbf'))
        tab_iter = mapping.TableView('locsiter10vscenfemul.dbf')
        tab_sumcmun = mapping.TableView('Sumarize_c_municipi.dbf')
        SetProgressorPosition(2)
        SetProgressorLabel(u"Proceso para manzanas:\nHaciendo joins necesarios al catálogo de manzanas..".encode('cp1254'))
        AddJoin_management(tab_mzs,"CVE_AGEBC",tab_agb,"AGEB","KEEP_ALL")
        AddJoin_management(tab_mzs,"cat_manzanas.CVE_LOCC",tab_iter,"CVE_ITER10","KEEP_ALL")
        SetProgressorPosition(3)
        AddJoin_management(tab_mzs,"cat_manzanas.CVE_MUNC",tab_sumcmun,"CVE_MUN","KEEP_ALL")
        flm = FieldMappings()
        flm.loadFromString(u'CVE_ENT "CVE_ENT" true true false 2 Text 0 0 ,First,#,{0},{0}.CVE_ENT,-1,-1;CVE_MUNC "CVE_MUNC" true true false 5 Text 0 0 ,First,#,{0},{0}.CVE_MUNC,-1,-1;CVE_AGEBC "CVE_AGEBC" true true false 13 Text 0 0 ,First,#,{0},{0}.CVE_AGEBC,-1,-1;NOM_ENT "NOM_ENT" true true false 45 Text 0 0 ,First,#,{0},{0}.NOM_ENT,-1,-1;NOM_MUN "NOM_MUN" true true false 110 Text 0 0 ,First,#,{0},{0}.NOM_MUN,-1,-1;NOM_LOC "NOM_LOC" true true false 120 Text 0 0 ,First,#,{0},{0}.NOM_LOC,-1,-1;AGEB_ID "AGEB_ID" true true false 9 Long 0 9 ,First,#,{0},{1}.AGEB_ID,-1,-1;CVE_MZAC "CVE_MZAC" true true false 16 Text 0 0 ,First,#,{0},{0}.CVE_MZAC,-1,-1;MANZANA_ID "MANZANA_ID" true true false 9 Long 0 9 ,First,#,{0},{0}.OID,-1,-1;ENTIDAD_ID "ENTIDAD_ID" true true false 2 Short 0 2 ,First,#,{0},{0}.CVE_ENT,-1,-1;MANZANA "MANZANA" true true false 3 Text 0 0 ,Last,#,{0},{0}.CVE_MZAC,13,15;MUN_ID "MUN_ID" true true false 5 Long 0 5 ,First,#,{0},{3}.MAX_C_MUN,-1,-1;CVE_LOCNUM "CVE_LOCNUM" true true false 4 Short 0 4 ,Last,#,{0},{0}.CVE_LOCC,5,8;CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},{2}.CVECEFEMUL,-1,-1;AGEB "AGEB" true true false 5 Text 0 0 ,Last,#,{0},{0}.CVE_AGEBC,9,12;'.format('cat_manzanas','cat_agebs','locsiter10vscenfemul','Sumarize_c_municipi'))

        SetProgressorLabel(u"Proceso para manzanas:\nCreando cat_manzanas_completo.dbf (Este paso puede tardar algunos minutos)..")
        SetProgressorPosition(4)
        TableToTable_conversion(tab_mzs,getcwd(),'cat_manzanas_completo.dbf',None,flm)
        SetProgressorLabel(u"Proceso para manzanas:\nCalculando campos..")
        SetProgressorPosition(5)
        RemoveJoin_management(tab_mzs)
        tab_mzs = mapping.TableView('cat_manzanas_completo.dbf')
        CalculateField_management(tab_mzs,"MANZANA_ID","!OID!+1","PYTHON")
        SetProgressorPosition(6)
        return

    def cps(self,parameters):
        SetProgressor("Step","Proceso para codigos postales:\nIniciando..",0,8,1)
        SetProgressorPosition(1)
        chdir(parameters[6].valueAsText)
        disp_movil.cat_cp(self)
        copy2('cat_cp.dbf','cat_cp_completo.dbf')
        SetProgressorLabel(u"Proceso para codigos postales:\nCreando cat_cp_completo.dbf..")
        SetProgressorPosition(6)
        tab_cp = mapping.TableView('cat_cp_completo.dbf')
        DeleteField_management(tab_cp,[u"C_CODIGO_P",u"CVE_CODIGO",u"NOM_CODIGO",u"C_MUN",u"FCH_INICIO",u"CVE_MUN"])
        SetProgressorPosition(7)
        copy2('cat_cp_completo.dbf',join(u'FINALES','cat_cp.dbf'))
        tab_cp = mapping.TableView(join(u'FINALES','cat_cp.dbf'))
        SetProgressorLabel(u"Proceso para codigos postales:\nCreando catálogo de codigos postales final..".encode('cp1254'))
        SetProgressorPosition(8)
        disp_movil.mapping_tab(self,tab_cp)
        ResetProgressor()
        del tab_cp
        return

    def cat_cp(self):
        mxd = mapping.MapDocument("CURRENT")
        tab_cp = mapping.ListTableViews(mxd,'cat_cp')[0]
        fields = [[u'ENTIDAD_ID', u'DOUBLE', 4, 0, 0],[u'MUN_ID', u'DOUBLE', 5, 0, 0],[u'CP', u'TEXT', 0, 0, 5],[u'ID_CP', u'DOUBLE', 20, 0, 0]]
        for fld in fields:
            AddField_management(tab_cp,*fld)
        SetProgressorLabel(u"Proceso para codigos postales:\nCalculando campos..")
        SetProgressorPosition(2)
        CalculateField_management(tab_cp,"ENTIDAD_ID","!CVE_MUNICI![:2]","PYTHON")
        tab_sumcmun = mapping.TableView('Sumarize_c_municipi.dbf')
        AddJoin_management(tab_cp,"CVE_MUNICI",tab_sumcmun,"CVE_MUN","KEEP_COMMON")
        SetProgressorPosition(3)
        CalculateField_management(tab_cp,"cat_cp.MUN_ID","!Sumarize_c_municipi.MAX_C_MUN!","PYTHON")
        RemoveJoin_management(tab_cp)
        SetProgressorPosition(4)
        CalculateField_management(tab_cp,"CP","!CVE_CODIGO!","PYTHON")
        SetProgressorPosition(5)
        CalculateField_management(tab_cp,"ID_CP","!C_CODIGO_P!","PYTHON")
        del mxd
        return

    def asentamientos(self,parameters):
        SetProgressor("Step","Proceso para asentamientos:\nIniciando..",0,6,1)
        SetProgressorPosition(1)
        chdir(parameters[6].valueAsText)
        disp_movil.cat_asentamientos(self)
        copy2('cat_asentamientos_completo.dbf',join('FINALES','cat_asentamientos.dbf'))
        SetProgressorLabel(u"Proceso para asentamientos:\nCreando catálogo de asentamientos final..".encode('cp1254'))
        SetProgressorPosition(5)
        tab_ase = mapping.TableView(join('FINALES','cat_asentamientos.dbf'))
        DeleteField_management(tab_ase,[u'C_ASENTAMI',u'CVE_ASENTA',u'C_CODIGO_P',u'FCH_INICIO'])
        SetProgressorPosition(6)
        disp_movil.mapping_tab(self,tab_ase)
        ResetProgressor()
        del tab_ase
        return

    def cat_asentamientos(self):
        mxd = mapping.MapDocument("CURRENT")
        tab_ase = mapping.ListTableViews(mxd,'cat_asentamientos')[0]
        SetProgressorPosition(2)
        tab_cp = mapping.TableView('cat_cp.dbf')
        AddJoin_management(tab_ase,"C_CODIGO_P",tab_cp,"ID_CP","KEEP_ALL")
        SetProgressorPosition(2)
        flm = FieldMappings()
        flm.loadFromString(u'C_ASENTAMI "C_ASENTAMI" true true false 9 Double 2 8 ,First,#,{0},{0}.C_ASENTAMI,-1,-1;CVE_ASENTA "CVE_ASENTA" true true false 5 Text 0 0 ,First,#,{0},{0}.CVE_ASENTA,-1,-1;C_CODIGO_P "C_CODIGO_P" true true false 8 Float 2 7 ,First,#,{0},{0}.C_CODIGO_P,-1,-1;FCH_INICIO "FCH_INICIO" true true false 8 Date 0 0 ,First,#,{0},{0}.FCH_INICIO,-1,-1;ASENTA_ID "ASENTA_ID" true true false 9 Long 0 9 ,First,#,{0},{0}.C_ASENTAMI,-1,-1;ENTIDAD_ID "ENTIDAD_ID" true true false 4 Short 0 4 ,First,#,{0},{1}.ENTIDAD_ID,-1,-1;MUN_ID "MUN_ID" true true false 5 Long 0 5 ,First,#,{0},{1}.MUN_ID,-1,-1;NOM_ASENTA "NOM_ASENTA" true true false 254 Text 0 0 ,First,#,{0},{0}.NOM_ASENTA,-1,-1;ID_CP "ID_CP" true true false 20 Double 0 20 ,First,#,{0},{0}.C_CODIGO_P,-1,-1'.format(tab_ase.name,tab_cp.name))
        SetProgressorPosition(3)
        SetProgressorLabel(u"Proceso para asentamientos:\nCreando cat_asentamientos_completo.dbf..")
        TableToTable_conversion(tab_ase,getcwd(),'cat_asentamientos_completo.dbf',None,flm)
        SetProgressorPosition(4)
        RemoveJoin_management(tab_ase)
        del tab_ase, tab_cp, flm, mxd
        return

    def vialidades(self,parameters):
        SetProgressor("Step","Proceso para vialidades:\nIniciando..",0,8,1)
        SetProgressorPosition(1)
        chdir(parameters[6].valueAsText)
        disp_movil.cat_vialidades(self)
        copy2('cat_vialidades_completo.dbf',join('FINALES','cat_vialidades.dbf'))
        SetProgressorLabel(u"Proceso para vialidades:\nCreando catálogo de vialidades final..".encode('cp1254'))
        SetProgressorPosition(7)
        tab_vial = mapping.TableView(join('FINALES','cat_vialidades.dbf'))
        DeleteField_management(tab_vial,[u'CVE_LOCC',u'CVE_ACT',u'CVE_MUNC'])
        SetProgressorPosition(8)
        disp_movil.mapping_tab(self,tab_vial)
        ResetProgressor()
        del tab_vial
        return

    def cat_vialidades(self):
        mxd = mapping.MapDocument("CURRENT")
        tab_vial = mapping.ListTableViews(mxd,'cat_vialidades_completo')[0]
        SetProgressorPosition(2)
        tab_eqv = mapping.TableView('equiv_vial_vs_cenfemul.dbf')
        tab_locact = mapping.TableView('LOC_ACT.dbf')
        SetProgressorLabel(u"Proceso para codigos vialidades:\nCalculando campos..")
        SetProgressorPosition(3)
        AddJoin_management(tab_vial,"CVE_LOCC",tab_eqv,"CVE_LOCC","KEEP_COMMON")
        CalculateField_management(tab_vial,"cat_vialidades_completo.CVE_ACT","!equiv_vial_vs_cenfemul.CVE_ACT!","PYTHON")
        SetProgressorPosition(4)
        RemoveJoin_management(tab_vial)
        AddJoin_management(tab_vial,"CVE_ACT",tab_locact,"CVE_LOC","KEEP_COMMON") 
        SetProgressorPosition(5)
        CalculateField_management(tab_vial,"cat_vialidades_completo.ID_LOC","!LOC_ACT.C_LOC!","PYTHON")
        SetProgressorPosition(6)
        RemoveJoin_management(tab_vial)
        del tab_vial, tab_locact, tab_eqv, mxd
        return

    def barrendero(self,pth):
        chdir(pth)
        for root, dirs, files in walk(".", topdown=False):
            for name in files:
                    if name.endswith('.xml'):
                            remove(join(root, name))
        return
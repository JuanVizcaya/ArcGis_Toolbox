# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function
from arcpy import Parameter, AddMessage, CreateUniqueName, mapping, AddField_management, CalculateField_management, AddJoin_management, RemoveJoin_management, DeleteField_management, RefreshActiveView, RefreshTOC, JoinField_management
from arcpy.da import InsertCursor, SearchCursor
from .utils import mktable, read_dbf
from xlrd import open_workbook
from xlutils.copy import copy
from shutil import copy2
from os import getcwd, chdir, remove, mkdir, listdir, walk
from os.path import join
from datetime import datetime

__all__ = ["sepomex"]

class sepomex(object):
    def __init__(self):
        self.__licens = "users"

    @property
    def _license(self):
        return True
        #return utils.license_v2(utils.licens.lists[self.__licens])
    
    @property
    def params(self):
        CPdwnld = Parameter('Catalogo_CP',u'Catálogo (CPdescarga.xls):'.encode('cp1254'),'Input','DEFile','Required')
        fch_act = Parameter('Checha_actual',u'Fecha de actualización (dd/mm/aaaa):'.encode('cp1254'),'Input','GPDate','Required')
        bef_dir = Parameter('berdir',u'Sepomex anterior (Carpeta "CATALOGO_SEPOMEX"):','Input','DEWorkspace','Required')
        svdir = Parameter('savedir',u'Ruta de salida (Carpeta "CATALOGO_MES_AAAA"):','Input','DEWorkspace','Required')
        C_muni = Parameter('C_MUNICI',u'Catálogo C_MUNICI (Sólo si fue actualizado)'.encode('cp1254'),'Input','GPTableView','Optional')
        CPdwnld.filter.list = ['xls']
        return [CPdwnld,bef_dir,svdir,fch_act,C_muni]

    def cat_sepo(self,book_dir,fch_act):
        fields_n = [[u'D_CODIGO', u'TEXT', 0, 0, 5], [u'D_ASENTA', u'TEXT', 0, 0, 57], [u'D_TIPO_ASE', u'TEXT', 0, 0, 21], [u'D_MNPIO', u'TEXT', 0, 0, 49], [u'D_ESTADO', u'TEXT', 0, 0, 31], [u'D_CIUDAD', u'TEXT', 0, 0, 49], [u'D_CP', u'DOUBLE', 5, 0, 5], [u'C_ESTADO', u'TEXT', 0, 0, 2], [u'C_OFICINA', u'DOUBLE', 5, 0, 5], [u'C_CP', u'DOUBLE', 1, 0, 1], [u'C_TIPO_ASE', u'DOUBLE', 2, 0, 2], [u'C_MNPIO', u'TEXT', 0, 0, 3], [u'ID_ASENTA_', u'DOUBLE', 4, 0, 4], [u'D_ZONA', u'TEXT', 0, 0, 10], [u'C_CVE_CIUD', u'DOUBLE', 2, 0, 2]]
        tab = mktable('unido_cp_sepomex_{0}_final.dbf'.format(fch_act.strftime('%d%b%y')),fields_n)
        book = open_workbook(book_dir)
        fields = [fld[0] for fld in fields_n]
        dat_edo = []
        with InsertCursor(tab,fields) as ic:
                for sheet in book.sheets()[1:]:
                    for i in xrange(1,sheet.nrows):
                        row = sheet.row_slice(i)
                        if row[9].value == '':
                            row[9].value = 0
                        if row[14].value == '':
                            row[14].value = 0
                        ic.insertRow((row[0].value,row[1].value.upper(),row[2].value,row[3].value,row[4].value,row[5].value,row[6].value,row[7].value,row[8].value,row[9].value,row[10].value,row[11].value,row[12].value,row[13].value,row[14].value))
                    dat_edo.append(sheet.nrows-1)
                    del i, row
                del sheet
        del tab, book, fields_n, fields, ic
        return dat_edo

    def dts_ord(self,datos, nfld):
        dats_ord = []
        for x in xrange(1,len(datos)):
            if datos[x][nfld] == datos[x-1][nfld]:
                pass
            else:
                dats_ord.append(datos[x-1])
        dats_ord.append(datos[x])
        del x
        return dats_ord

    def val_x_edo(self,bef_dir,fch_act,dat_edo):
        book = open_workbook(join(bef_dir,'VERIFICAR_TOTALES_POR_ESTADO.xls'))
        sheet = book.sheet_by_index(0)
        num_cols = sheet.ncols
        wbook = copy(book)
        wsheet = wbook.get_sheet(0)
        wsheet.write(0,num_cols,fch_act.strftime('%d/%b/%y').upper())
        for i in xrange(1,len(dat_edo)+1):
            wsheet.write(i,num_cols,dat_edo[-i])
        suma = sum(dat_edo)
        wsheet.write(len(dat_edo)+1,num_cols,suma)
        wbook.save('VERIFICAR_TOTALES_POR_ESTADO.xls')
        del wbook, suma, i, dat_edo, num_cols, book, sheet, wsheet

    def ayb_cp(self,dts_mun,dts_spmx,dts_cdg,fch_act):
        fields_cpb = [[u'C_CODIGO_P', u'DOUBLE', 7, 2, 8],[u'CVE_CODIGO', u'TEXT', 0, 0, 5],[u'NOM_CODIGO', u'TEXT', 0, 0, 5],[u'C_MUNICIPI', u'FLOAT', 7, 2, 8],[u'FCH_INICIO', u'DATE', 0, 0, 8],[u'CVE_MUNICI', u'TEXT', 0, 0, 5],[u'FCH_FIN', u'DATE', 0, 0, 8],[u'TEMP', u'TEXT', 0, 0, 1],[u'COM_CPMUN', u'TEXT', 0, 0, 100],[u'FCH_FINA_1', u'DATE', 0, 0, 8],[u'COM_CPMU_1', u'TEXT', 0, 0, 100],[u'FCH_FINA_2', u'DATE', 0, 0, 8]]
        fields_cpa = [[u'C_CODIGO_P', u'DOUBLE', 18, 5, 19],[u'CVE_CODIGO', u'TEXT', 0, 0, 5],[u'NOM_CODIGO', u'TEXT', 0, 0, 5],[u'C_MUNICIPI', u'DOUBLE', 18, 5, 19],[u'FCH_INICIO', u'DATE', 0, 0, 8],[u'FCH_FIN', u'DATE', 0, 0, 8],[u'CVE_MUNICI', u'TEXT', 0, 0, 5],[u'FCH_SISTEM', u'DATE', 0, 0, 8],[u'USUARIO_CA', u'TEXT', 0, 0, 80],[u'ESTATUS', u'DOUBLE', 18, 5, 19]]
        tab_b = mktable('TABLA_BAJAS_CP.dbf',fields_cpb)
        tab_a = mktable('TABLA_ALTAS_CP.dbf',fields_cpa)
        fnd_cmun = [dt[4] for dt in dts_mun]
        fields_b = [fld[0] for fld in fields_cpb]
        fields_a = [fld[0] for fld in fields_cpa]
        del fields_cpa
        buf_ccod = []
        for datos in dts_cdg:
            buf_ccod.append(datos[1])
        buf_ccod.sort()
        last_ccod = buf_ccod[len(buf_ccod)-1]
        del buf_ccod
        with InsertCursor(tab_b,fields_b) as ic_b:
            with InsertCursor(tab_a,fields_a)as ic_a:
                n = len(dts_cdg)
                if len(dts_cdg) < len(dts_spmx):
                    n = len(dts_spmx)
                i = 0
                j = 0
                while(i < n and j < n):
                    if dts_spmx[i][16] == dts_cdg[j][7]:
                        i += 1
                        j += 1
                    elif dts_spmx[i][16] not in [fld[7] for fld in dts_cdg[j:j+300]]:
                        last_ccod += 1
                        if dts_spmx[i][8]+dts_spmx[i][12] in fnd_cmun:
                            ind = fnd_cmun.index(dts_spmx[i][8]+dts_spmx[i][12])
                            row4 = dts_mun[ind][2]
                        else:
                            row4 = ''
                        ic_a.insertRow((last_ccod,dts_spmx[i][1],dts_spmx[i][1],row4,fch_act.strftime('%d/%m/%Y'),None,dts_spmx[i][8]+dts_spmx[i][12],None,'',1))
                        AddMessage ('Alta: {0}'.format(dts_spmx[i][16]))
                        i += 1
                    elif dts_cdg[j][7] not in [fld[16] for fld in dts_spmx[i:i+300]]:
                        ic_b.insertRow((dts_cdg[j][1],dts_cdg[j][2],dts_cdg[j][3],dts_cdg[j][4],dts_cdg[j][5],dts_cdg[j][6],fch_act.strftime('%d/%m/%Y'),'A','',None,'',None))
                        AddMessage ('Baja: {0}'.format(dts_cdg[j][7]))
                        j += 1
        del dts_spmx, dts_cdg, i, j, n, tab_a, tab_b, ic_b, ic_a, last_ccod, fields_a, fields_b
        return fields_cpb

    def ayb_ase(self,dts_spmx,dts_ase,fch_act,dir_alts):
        fields_asb = [[u'C_ASENTAMI', u'DOUBLE', 8, 2, 9],[u'CVE_ASENTA', u'TEXT', 0, 0, 5],[u'NOM_ASENTA', u'TEXT', 0, 0, 254],[u'C_CODIGO_P', u'FLOAT', 7, 2, 8],[u'FCH_INICIO', u'DATE', 0, 0, 8],[u'ASENCPMUN', u'TEXT', 0, 0, 150],[u'FCH_FINAL', u'DATE', 0, 0, 8]]
        fields_asa = [[u'ASENCPMUN', u'TEXT', 0, 0, 150],[u'C_ASENTAMI', u'DOUBLE', 18, 5, 19],[u'CVE_ASENTA', u'TEXT', 0, 0, 8],[u'NOM_ASENTA', u'TEXT', 0, 0, 254],[u'C_CODIGO_P', u'DOUBLE', 18, 5, 19],[u'FCH_INICIO', u'DATE', 0, 0, 8],[u'FCH_FINAL', u'DATE', 0, 0, 8],[u'FCH_SISTEM', u'DATE', 0, 0, 8],[u'USUARIO_CA', u'TEXT', 0, 0, 80],[u'ESTATUS', u'DOUBLE', 18, 5, 19],[u'CVE_CODIGO', u'TEXT', 0, 0, 5]]
        tab_b = mktable('TABLA_BAJAS_ASENTAMIENTOS.dbf',fields_asb)
        m_dir = getcwd()
        chdir(dir_alts)
        tab_a = mktable('TABLA_ALTAS_ASENTAMIENTOS2.dbf',fields_asa)
        chdir(m_dir)
        fields_b = [fld[0] for fld in fields_asb]
        fields_a = [fld[0] for fld in fields_asa]
        del fields_asb, fields_asa

        with InsertCursor(tab_b,fields_b) as ic_b:
            with InsertCursor(tab_a,fields_a)as ic_a:
                n = len(dts_ase)
                if len(dts_ase) < len(dts_spmx):
                    n = len(dts_spmx)
                i = 0
                j = 0
                while(i < n and j < n):
                    if dts_spmx[i][17] == dts_ase[j][6]:
                        i += 1
                        j += 1
                    elif dts_spmx[i][17] not in [fld[6] for fld in dts_ase[j:j+500]]:
                        ic_a.insertRow((dts_spmx[i][17],0,'',dts_spmx[i][2],dts_spmx[i][18],fch_act,None,None,'',1,dts_spmx[i][1]))
                        AddMessage ('Alta: {0}'.format(dts_spmx[i][17]))
                        i += 1
                    elif dts_ase[j][6] not in [fld[17] for fld in dts_spmx[i:i+500]]:
                        ic_b.insertRow((dts_ase[j][1],dts_ase[j][2],dts_ase[j][3],dts_ase[j][4],dts_ase[j][5],'',fch_act))
                        AddMessage ('Baja: {0}'.format(dts_ase[j][6]))
                        j += 1
                del n, i, j
        del ic_b, ic_a, fields_b, fields_a, 
        return

    def trash(self,maindir):
        chdir(maindir)
        for root, dirs, files in walk(".", topdown=False):
            for name in files:
                    if name.endswith('.xml'):
                            remove(join(root, name))
        return

    def process(self, parameters):
        bef_dir = parameters[1].valueAsText
        main_path = parameters[2].valueAsText
        fech  = parameters[3].valueAsText.split(' ')[0]
        fch_act = datetime.strptime(fech,'%d/%m/%Y')
        AddMessage("Creando el directorio..")
        chdir(main_path)
        main_dir = CreateUniqueName(join(main_path,'CATALOGO_SEPOMEX'))
        mkdir(main_dir)
        chdir(main_dir)
        dirs = ['01-ORIGINAL_SEPOMEX_POR_ESTADO','02-ORIGINAL_SEPOMEX','03-TABLAS_BASE_PROGRAMA','04-TABLAS_A_UTILIZAR_EN_EL_PROGRAMA','05-PROCESO_CP','06-PROCESO_ASENTAMIENTOS','07-TABLAS_FINALES']
        for pat in dirs:
            mkdir(pat)
        del pat
        AddMessage("Creando Sepomex dbf unido..")
        chdir(dirs[1])
        dat_edo = sepomex.cat_sepo(self,parameters[0].valueAsText,fch_act)
        AddMessage("Creando archivo: Valores por estado xls")
        chdir(main_dir)
        sepomex.val_x_edo(self,bef_dir,fch_act,dat_edo)
        AddMessage("Copiando archivos necesarios..")
        copy2(parameters[0].valueAsText, join(dirs[0], 'CPdescarga.xls'))
        chdir(dirs[2])
        for i in xrange(len(listdir(bef_dir))):
            if '11-CATALOGOS' in listdir(bef_dir)[i]:
                carp = listdir(bef_dir)[i]
        del i
        copy2(join(main_dir, dirs[1],u'unido_cp_sepomex_{0}_final.dbf'.format(fch_act.strftime('%d%b%y'))),u'sepomex_{0}_tablac.dbf'.format(fch_act.strftime('%d%b%y')))
        copy2(join(bef_dir,carp,'C_ASENTA.dbf'), 'C_ASENTA.dbf')
        copy2(join(bef_dir,carp,'C_CODIGO.dbf'), 'C_CODIGO.dbf')
        if not parameters[4].value:
            copy2(join(bef_dir,dirs[2],'C_MUNICI.dbf'), 'C_MUNICI.dbf')
        else:
            copy2(join(mapping.TableView(parameters[4].valueAsText).workspacePath,'{0}.dbf'.format(parameters[4].valueAsText)),'C_MUNICI.dbf')
        dts_mun = read_dbf('C_MUNICI.dbf','CVE_MUN')
        #dts_mun = read_dbf('C_MUNICI.dbf','CVE_MUNICI')
        chdir(join(main_dir, dirs[3]))
        copy2(join(main_dir, dirs[1],u'unido_cp_sepomex_{0}_final.dbf'.format(fch_act.strftime('%d%b%y'))),u'catalogo_cp_sepomex.dbf')
        copy2(join(bef_dir,carp,'C_ASENTA.dbf'), 'C_ASENTA.dbf')
        copy2(join(bef_dir,carp,'C_CODIGO.dbf'), 'C_CODIGO.dbf')
        AddMessage("Agregando campos necesarios a C_CODIGO..")
        tab = mapping.TableView('C_CODIGO.dbf')
        for fld in [[u'COM_CPMUN', u'TEXT', 0, 0, 100],[u'FCH_FINAL', u'DATE', None, None, 8],[u'TEMP', u'TEXT', 0, 0, 1]]:
            AddField_management(tab,*fld)
        CalculateField_management(tab,'COM_CPMUN', """!CVE_CODIGO! +"_"+ !CVE_MUNICI!""","PYTHON_9.3")
        CalculateField_management(tab,'TEMP', """'A'""","PYTHON_9.3")
        del tab, fld
        AddMessage("Agregando campos necesarios a Catalogo CP..")
        tab = mapping.TableView('catalogo_cp_sepomex.dbf')
        tab_c = mapping.TableView('C_CODIGO.dbf')
        for fld in [[u'COM_CPMUN', u'TEXT', 0, 0, 100],[u'ASENCPMUN', u'TEXT', 0, 0, 150]]:
            AddField_management(tab,*fld)
        CalculateField_management(tab,'COM_CPMUN', """!D_CODIGO! +"_"+ !C_ESTADO!+ !C_MNPIO!""","PYTHON_9.3")
        CalculateField_management(tab,'ASENCPMUN', """!D_ASENTA! +"_"+ !COM_CPMUN!""","PYTHON_9.3")
        del tab, fld
        AddMessage("Agregando campos necesarios a C_ASENTA..")
        tab_a = mapping.TableView('C_ASENTA.dbf')
        JoinField_management(tab_a,'C_codigo_p', tab_c,'C_codigo_p','COM_CPMUN')
        AddField_management(tab_a,*[u'ASENCPMUN', u'TEXT', 0, 0, 150])
        CalculateField_management(tab_a,'ASENCPMUN',"""!NOM_ASENTA!+'_'+!COM_CPMUN!""","PYTHON_9.3")
        DeleteField_management(tab_a, 'COM_CPMUN')
        del tab_a
        AddMessage("Creando Tablas Altas & Bajas CP..")
        dts_cdg = read_dbf('C_CODIGO.dbf','COM_CPMUN')
        dts_spmx = read_dbf('catalogo_cp_sepomex.dbf','COM_CPMUN')
        dts_spmx = sepomex.dts_ord(self,dts_spmx,16)
        chdir(join(main_dir, dirs[6]))
        fields_cpb = sepomex.ayb_cp(self,dts_mun,dts_spmx,dts_cdg,fch_act)
        del dts_cdg, dts_spmx, dts_mun
        AddMessage("Join de C_codigo_p al catalogo sepomex..")
        tab_cpa = mapping.TableView('TABLA_ALTAS_CP.dbf')
        chdir(join(main_dir, dirs[3]))
        tab_spmx = mapping.TableView('catalogo_cp_sepomex.dbf')
        AddField_management(tab_spmx,*[u'C_CODIGO_P', u'DOUBLE', 18, 5, 19])
        AddJoin_management(tab_spmx,"D_CODIGO",tab_c,"Cve_codigo","KEEP_COMMON")
        CalculateField_management(tab_spmx,"catalogo_cp_sepomex.C_CODIGO_P","!C_CODIGO.C_codigo_p!","PYTHON")
        RemoveJoin_management(tab_spmx)
        AddJoin_management(tab_spmx,"D_CODIGO",tab_cpa,"CVE_CODIGO","KEEP_COMMON")
        CalculateField_management(tab_spmx,"catalogo_cp_sepomex.C_CODIGO_P","!TABLA_ALTAS_CP.C_CODIGO_P!","PYTHON")
        RemoveJoin_management(tab_spmx)
        del tab_spmx, tab_c, tab_cpa
        AddMessage("Creando Tablas Altas & Bajas Asentamientos..")
        chdir(join(main_dir, dirs[3]))
        dts_ase = read_dbf('C_ASENTA.dbf','ASENCPMUN')
        dts_spmx = read_dbf('catalogo_cp_sepomex.dbf','ASENCPMUN')
        dts_spmx = sepomex.dts_ord(self,dts_spmx,17)
        chdir(join(main_dir, dirs[6]))
        sepomex.ayb_ase(self,dts_spmx,dts_ase,fch_act,join(main_dir,dirs[5]))
        del dts_spmx, dts_ase
        copy2(join(main_dir,dirs[5],'TABLA_ALTAS_ASENTAMIENTOS2.dbf'), 'TABLA_ALTAS_ASENTAMIENTOS.dbf')
        tab = mapping.TableView('TABLA_ALTAS_ASENTAMIENTOS.dbf')
        DeleteField_management(tab,['ASENCPMUN','CVE_CODIGO'])
        AddMessage("Cargando archivos a SAC..")
        fch_carp = fch_act.strftime('%d%b%y').upper()
        carp = ('CARGAR_A_SAC_{0}'.format(fch_carp))
        mkdir(carp)
        copy2('TABLA_ALTAS_CP.dbf', join(carp,'TABLA_ALTAS_CP_{0}.dbf'.format(fch_carp)))
        tab = mapping.TableView(join(carp,'TABLA_ALTAS_CP_{0}.dbf'.format(fch_carp)))
        DeleteField_management(tab,['FCH_FIN','FCH_SISTEM','USUARIO_CA','ESTATUS'])

        copy2('TABLA_ALTAS_ASENTAMIENTOS.dbf', join(carp,'TABLA_ALTAS_ASENTAMIENTOS_{0}.dbf'.format(fch_carp)))
        tab = mapping.TableView(join(carp,'TABLA_ALTAS_ASENTAMIENTOS_{0}.dbf'.format(fch_carp)))
        DeleteField_management(tab,['CVE_ASENTAMI','C_ASENTAMI','CVE_ASENTA','FCH_FINAL','FCH_SISTEM','USUARIO_CA','ESTATUS'])

        copy2('TABLA_BAJAS_ASENTAMIENTOS.dbf', join(carp,'TABLA_BAJAS_ASENTAMIENTOS_{0}.dbf'.format(fch_carp)))
        tab_asb = mapping.TableView(join(carp,'TABLA_BAJAS_ASENTAMIENTOS_{0}.dbf'.format(fch_carp)))
        DeleteField_management(tab_asb,'ASENCPMUN') 

        tab = mapping.TableView('TABLA_BAJAS_CP.dbf')
        chdir(carp)
        fields_cpb1 = fields_cpb[:5]
        fields_cpb1.append(fields_cpb[6])
        fields_cpb1.append(fields_cpb[5])
        tab1 = mktable('TABLA_BAJAS_CP_{0}.dbf'.format(fch_carp), fields_cpb1)
        DeleteField_management(tab1,['TEMP','COM_CPMUN','FCH_FINA_1','COM_CPMU_1','FCH_FINA_2'])

        fs = [fld[0] for fld in fields_cpb]
        fs1 = [fld[0] for fld in fields_cpb1]
        del fields_cpb1, fields_cpb, fch_carp, carp

        with SearchCursor(tab,fs) as sc:
            with InsertCursor(tab1,fs1) as ic:
                for row in sc:
                    ic.insertRow((row[0],row[1],row[2],row[3],row[4],row[6],row[5]))

        mxd =  mapping.MapDocument("CURRENT")
        df = mapping.ListDataFrames(mxd, "*")[0]
        for arch in listdir(getcwd()):
            if arch.endswith('.dbf'):
                mapping.AddTableView(df,mapping.TableView(arch))
        del fs, fs1, tab, tab1, sc, ic, mxd, df
        RefreshActiveView()
        RefreshTOC()
        AddMessage("Borrando archivos innecesarios..")
        sepomex.trash(self,main_dir)
        return
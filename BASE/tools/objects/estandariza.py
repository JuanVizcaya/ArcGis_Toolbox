# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from arcpy import mapping, RefreshActiveView, RefreshTOC, Parameter, AddMessage, SetProgressorLabel, AddWarning, SpatialReference, MakeXYEventLayer_management, Project_management, env, Statistics_analysis
from arcpy.da import InsertCursor, SearchCursor
from os import chdir, getcwd, mkdir, listdir, remove, walk
from os.path import join, isdir
from shutil import copy2
from urllib import urlopen
from re import search
from datetime import datetime
from zipfile import ZipFile
from utils import mktable, comas, read_dbf

__all__ = ["est_cenf"]

class est_cenf(object):
    def __init__(self):
        self.__licens = "users"

    def mapping_file(self,map_file):
        mxd =  mapping.MapDocument("CURRENT")
        df = mapping.ListDataFrames(mxd, "*")[0]
        try:
            mapping.AddTableView(df,map_file)
        except:
            mapping.AddLayer(df,map_file,"AUTO_ARRANGE")
            RefreshActiveView()
        RefreshTOC()

    @property
    def barrendero(self):
        chdir(self.current)
        for root, dirs, files in walk(".", topdown=False):
            for name in files:
                    if name.endswith('.xml') or name.endswith('.sbn') or name.endswith('.sbx'):
                            remove(join(root, name))
        return

    @property
    def _license(self):
        return True
        #return utils.license_v2(utils.licens.lists[self.__licens])
    
    @property
    def params(self):
        cnfml = Parameter('cenfemul',u'Catálogo "NOMBRE_MMMAA"  (CSV File):'.encode("cp1254"),'Input','DEFile','Optional')
        cnfmlsv = Parameter('cenfemulsave','Guardar como:','Input','String','Optional',False)
        rgs = Parameter('regs',u'Registro de actualización (CSV File):'.encode("cp1254"),'Input','DEFile','Optional')
        rgssv = Parameter('regssave','Guardar como:','Input','String','Optional',False)
        tbls = Parameter('tablas','Tabla de equivalencia (CSV File):','Input','DEFile','Optional')
        tblssv = Parameter('tablassave','Guardar como:','Input','String','Optional',False)
        svdir = Parameter('savedir','Ruta de salida:','Input','DEWorkspace','Required')
        mkshp = Parameter('mkshp','Crear ShapeFile(s)','Input','GPBoolean','Optional',False)
        dwnlp = Parameter('dwnlp','Crear Reporte (INEGI)','Input','GPBoolean','Optional')
        shpstr = Parameter('shpstr','Archivos de programas sociales','Input','GPBoolean','Optional',False)
        rep = Parameter('rep','Crear reporte de registros actualizados','Input','GPBoolean','Optional')
        #reg_ant = Parameter('reg_ant',u'Registro de actualización del mes anterior (DBF File)'.encode("cp1254"),'Input','DEFile','Optional',False)
        cnfml.filter.list = ['csv']
        rgs.filter.list = ['csv']
        tbls.filter.list = ['csv']
        #reg_ant.filter.list = ['dbf']
        params = [cnfml,cnfmlsv,rgs,rgssv,tbls,tblssv,svdir,mkshp,dwnlp,shpstr,rep]
        return params

    def Makedir(self,parameters):
        for cat in [parameters[0],parameters[2],parameters[4]]:
            if cat.value:
                nom_cat = cat.valueAsText.split('\\')[-1].split('_')[-1][:-4]
                self.fech = datetime.strptime('{0}-{1}'.format(nom_cat[:-2],nom_cat[3:]),'%b-%y')
                break
        chdir(parameters[6].valueAsText)
        maindir = getcwd()
        if parameters[0].value:
            nom_dir = '{0}_CATALOGO_{1}_{2}'.format(self.fech.strftime('%Y%m'),self.fech.strftime('%B').upper(),self.fech.strftime('%Y'))
            while nom_dir in listdir(getcwd()):
                nom_dir = '{0}_{1}'.format(nom_dir, 'copy')
            mkdir(nom_dir)
            chdir(join(getcwd(),nom_dir))
            maindir = getcwd()
        mkdir('CATALOGO_A_ENTREGAR')
        if parameters[9].value:
            mkdir('CATALOGO_A_ENTREGAR\\PROGRAMAS_SOCIALES')
        mkdir('ORIGINALES_BAJADOS_DE_INTERNET')
        dwnl_dir = join(getcwd(),'ORIGINALES_BAJADOS_DE_INTERNET')
        mkdir('ORIGINALES_BAJADOS_DE_INTERNET\\ORIGINALES')
        chdir('ORIGINALES_BAJADOS_DE_INTERNET\\ORIGINALES')
        for arch,i in zip([parameters[0],parameters[2],parameters[4]],[1,3,5]):
            if arch.value:
                copy2(arch.valueAsText,arch.valueAsText.split('\\')[-1])
        chdir(join(maindir,'CATALOGO_A_ENTREGAR'))
        self.current = getcwd()
        return dwnl_dir

    def dwnl_cats(self,current):
        url_dwnl = 'http://geoweb.inegi.org.mx/mgn2kData/catalogos/'
        url_inf = 'http://geoweb.inegi.org.mx/mgn2k/catalogo.jsp'
        if not isdir(current):
            mkdir(current)
        chdir(current)
        mkdir('PREDEFINIDO')
        chdir(join(getcwd(),'PREDEFINIDO'))
        resp = urlopen(url_inf)
        lines = resp.readlines()
        def fec(date):
            mes_num = date.split('/')[-2]
            mes_str = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE",]
            return [date.split('/')[-3],mes_str[int(mes_num)-1],date.split('/')[-1]]
        with open('LEEME.txt', 'wb') as txtf:
            jl = '\r\n\r\n'
            for title in ['de Localidades Nacional','de Municipios Nacional']:
                i = 0
                for line in lines:
                    if search(title, line):
                        AddMessage(u"Descargando información de Catálogo {0}..".format(title).encode('cp1254'))
                        nom_arch = lines[i-3].split('/')[-3].split("'")[-2]
                        fch_arch = lines[i-2].split('>')[-2].split('<')[-2]
                        len_arch = lines[i-1].split('>')[-2].split('<')[-2]
                        desc = (u'Catálogo {0}'.format(title))
                        fch_corte= lines[i+1].split('>')[-2].split('<')[-2]
                        fch_ver = fec(fch_arch)
                        txtf.write(u'\t====================================================\r\n')
                        txtf.write(u'\t======= VESIÓN SUBIDA EL {0} DE {1} DEL {2} ======= \r\n'.format(fch_ver[2],fch_ver[1],fch_ver[0]).encode('cp1254'))
                        txtf.write(u'\t==================== {0} ===================={1}'.format(title.split(' ')[1].upper(),jl))
                        txtf.write(u'NOMBRE DEL ARCHIVO: {0}{1}'.format(nom_arch.upper(),jl))
                        txtf.write(u'FECHA DE ARCHIVO: {0}{1}'.format(fch_arch,jl))
                        txtf.write(u'TAMAÑO EN KB: {0}{1}'.format(len_arch,jl).encode('cp1254'))
                        txtf.write(u'DESCRIPCIÓN: {0}{1}'.format(desc,jl).encode('cp1254'))
                        txtf.write(u'FECHA DE CORTE: {0}{1}'.format(fch_corte,jl))
                        try:
                            url = join(url_dwnl,nom_arch)
                            u = urlopen(url)
                            with open(nom_arch, 'wb') as f:
                                metdat = u.info()
                                fsize = int(metdat.getheaders("Content-Length")[0])
                                AddMessage("Descargando: {0} Bytes: {1}".format(nom_arch, fsize))
                                fsize_dl = 0
                                block_sz = fsize/10
                                while True:
                                    buffer = u.read(block_sz)
                                    if not buffer:
                                        break
                                    fsize_dl += len(buffer)
                                    f.write(buffer)
                                    SetProgressorLabel("Descargado: {0} bytes  [{1}%]".format(fsize_dl, fsize_dl*100/fsize))
                                AddMessage("Archivo: {0}, Guardado".format(nom_arch))
                            SetProgressorLabel("Descomprimiendo {0}..".format(nom_arch))
                            with ZipFile(nom_arch) as arch_zip:
                                arch_zip.extractall(getcwd())
                            AddMessage("Archivo {0} descomprimido".format(nom_arch))
                        except:
                            AddWarning('el archivo "{0}" no está disponible para su descarga'.format(nom_arch))
                        break
                    i += 1
            AddMessage("Archivo: LEEME.txt Guardado")
            return

    def read_csv(self,arch):
        recini = [134,134,92,183]
        with open(arch,'r') as op:
            records = [row.decode('cp1254').replace(u'","',u'"|"').replace(u'À',u'Á').replace(u'È',u'É').replace(u'Ì',u'Í').replace(u'Ò',u'Ó').replace(u'Ù',u'Ú').replace(u'null',u'')[:-1] for row in op]
            #records = [row.decode('cp1254').replace(u'","',u'"|"').replace(u'\xc0',u'\xc1').replace(u'\xc8',u'\xc9').replace(u'\xcc',u'\xcd').replace(u'\xd2',u'\xd3').replace(u'\xd9',u'\xda').replace(u'null',u'')[:-1] for row in op]
        records[0]=records[0][recini[self.tipo]:]
        self.recs= [[eval(i) for i in row.split('|')] for row in records]
        del recini, records, row
        return

    def Stand(self,arch,tipo,parameters):
        chdir(self.current)
        self.tipo = tipo
        if tipo != 1:
            est_cenf.read_csv(self,arch)
        if tipo == 0:
            self.nlocs = len(self.recs)
        nom_arch = [parameters[1].valueAsText,parameters[1].valueAsText,parameters[3].valueAsText,parameters[5].valueAsText]
        current = getcwd()
        if tipo == 1:
            chdir('PROGRAMAS_SOCIALES')
        flds_save = ([[u'CVE_ENT', u'TEXT', 0, 0, 2], [u'CVE_MUNC', u'TEXT', 0, 0, 5], [u'CVE_LOCC', u'TEXT', 0, 0, 9], [u'NOM_ENT', u'TEXT', 0, 0, 110], [u'ABR_ENT', u'TEXT', 0, 0, 16], [u'NOM_MUN', u'TEXT', 0, 0, 110], [u'NOM_LOC', u'TEXT', 0, 0, 110], [u'AMBITO', u'TEXT', 0, 0, 1], [u'CVE_CARTA', u'TEXT', 0, 0, 6], [u'PLANO', u'TEXT', 0, 0, 1], [u'LATITUD', u'TEXT', 0, 0, 10], [u'LONGITUD', u'TEXT', 0, 0, 11], [u'LAT_DEC', u'DOUBLE', 12, 8, 13], [u'LON_DEC', u'DOUBLE', 14, 8, 15], [u'ALTITUD', u'TEXT', 0, 0, 4], [u'P_TOTAL', u'DOUBLE', 11, 0, 11], [u'P_MAS', u'DOUBLE', 11, 0, 11], [u'P_FEM', u'DOUBLE', 11, 0, 11], [u'V_TOT', u'DOUBLE', 11, 0, 11]],[[u'CVE_ENT', u'TEXT', 0, 0, 2], [u'CVE_MUNC', u'TEXT', 0, 0, 5], [u'CVE_LOCC', u'TEXT', 0, 0, 9], [u'NOM_ENT', u'TEXT', 0, 0, 110], [u'ABR_ENT', u'TEXT', 0, 0, 16], [u'NOM_MUN', u'TEXT', 0, 0, 110], [u'NOM_LOC', u'TEXT', 0, 0, 110], [u'AMBITO', u'TEXT', 0, 0, 1], [u'CVE_CARTA', u'TEXT', 0, 0, 6], [u'PLANO', u'TEXT', 0, 0, 1], [u'LATITUD', u'TEXT', 0, 0, 10], [u'LONGITUD', u'TEXT', 0, 0, 11], [u'LAT_DEC', u'DOUBLE', 11, 8, 12], [u'LON_DEC', u'DOUBLE', 13, 8, 14], [u'ALTITUD', u'TEXT', 0, 0, 4], [u'P_TOTAL', u'TEXT', 0, 0, 10], [u'P_MAS', u'TEXT', 0, 0, 10], [u'P_FEM', u'TEXT', 0, 0, 10], [u'V_TOT', u'TEXT', 0, 0, 10]],[[u'CVE_ENT', u'TEXT', 0, 0, 2], [u'CVE_MUNC', u'TEXT', 0, 0, 5], [u'CVE_LOCC', u'TEXT', 0, 0, 9], [u'NOM_ENT', u'TEXT', 0, 0, 110], [u'NOM_ABR', u'TEXT', 0, 0, 32], [u'NOM_MUN', u'TEXT', 0, 0, 110], [u'NOM_LOC', u'TEXT', 0, 0, 110], [u'DESCGO_ACT', u'TEXT', 0, 0, 80], [u'CGO_ACT', u'TEXT', 0, 0, 2],[u'AMBITO', u'TEXT', 0, 0, 1], [u'FECHA_ACT', u'TEXT', 0, 0, 10]],[[u'CVELOCCACT', u'TEXT', 0, 0, 9], [u'CVELOCCORI', u'TEXT', 0, 0, 9], [u'FECHA_ACT', u'TEXT', 0, 0, 10], [u'DESCGO_ACT', u'TEXT', 0, 0, 80], [u'CGO_ACT', u'TEXT', 0, 0, 2], [u'NOMLOC_ACT', u'TEXT', 0, 0, 110], [u'NOMLOC_ORI', u'TEXT', 0, 0, 110], [u'AMBLOC_ACT', u'TEXT', 0, 0, 1], [u'AMBLOC_ORI', u'TEXT', 0, 0, 1],[u'NOMMUN_ACT', u'TEXT', 0, 0, 110], [u'NOMMUN_ORI', u'TEXT', 0, 0, 110], [u'NOMENT_ACT', u'TEXT', 0, 0, 110], [u'NOMENT_ORI', u'TEXT', 0, 0, 110], [u'CVEMUNCACT', u'TEXT', 0, 0, 5], [u'CVEMUNCORI', u'TEXT', 0, 0, 5], [u'CVEENT_ACT', u'TEXT', 0, 0, 2], [u'CVEENT_ORI', u'TEXT', 0, 0, 2]])                      
        tab = mktable(nom_arch[tipo],flds_save[tipo])
        fields = [fld[0] for fld in flds_save[tipo]]
        with InsertCursor(tab,fields) as ic:
                SetProgressorLabel("Llenando campos..")
                if tipo == 0:
                    for row in self.recs:
                        ic.insertRow((row[0],row[0]+row[3],row[0]+row[3]+row[5],row[1],row[2],row[4],row[6],row[7],row[13],row[14],row[8],row[9],row[10],row[11],row[12],row[15].replace(u'*',u'0').replace(u'-',u'0'),row[16].replace(u'*',u'0').replace(u'-',u'0'),row[17].replace(u'*',u'0').replace(u'-',u'0'),row[18].replace(u'*',u'0').replace(u'-',u'0')))
                elif tipo == 1:
                    for row in self.recs:
                        ic.insertRow((row[0],row[0]+row[3],row[0]+row[3]+row[5],row[1],row[2],row[4],row[6],row[7],row[13],row[14],row[8],row[9],row[10],row[11],row[12],row[15],row[16],row[17],row[18]))
                elif tipo == 2:
                    for row in self.recs:
                        ic.insertRow((row[0],row[0]+row[3],row[0]+row[3]+row[5],row[1],row[2],row[4],row[6],row[10].upper(),row[9],row[7],row[8]))
                elif tipo == 3:
                    for row in self.recs:
                        ic.insertRow((row[7]+row[9]+row[11],row[0]+row[2]+row[4],row[14],row[16].upper(),row[15],row[12],row[5],row[13],row[6],row[10],row[3],row[8],row[1],row[7]+row[9],row[0]+row[2],row[7],row[0]))
        AddMessage(u"El archivo {0} Está listo!".format(nom_arch[tipo]).encode("cp1254"))
        self.table = mapping.TableView("{0}".format(nom_arch[tipo]))
        if tipo == 3:
            self.tab_eqv = self.table
        if not tipo in [0,1] or not parameters[9].value:
            est_cenf.mapping_file(self,self.table)
        del flds_save, tipo, row, tab, ic, nom_arch
        return 

    def mkshape(self):
        # Creando Shapefile(s)
        if self.tipo in [0,1]:
            env.workspace = getcwd()
            sr = SpatialReference()
            sr.loadFromString(u"PROJCS['Lambert',GEOGCS['GCS_ITRF_1992',DATUM['D_ITRF_1992',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-102.0],PARAMETER['Standard_Parallel_1',17.5],PARAMETER['Standard_Parallel_2',29.5],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',12.0],UNIT['Meter',1.0]];-37031600 -25743800 113924041.206794;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
            env.overwriteOutput = True
            MakeXYEventLayer_management(self.table,'LON_DEC','LAT_DEC','Lyr','ITRF 1992')
            AddMessage("Creando ShapeFile en {0}..".format(getcwd().split('\\')[-1]))
            Project_management('Lyr','CATALOGO_CENFEMUL_{0}.shp'.format(self.fech.strftime('%b%y').upper()),sr)
            remove("{0}.dbf".format(self.table.name))
            #utils.arcpy.AddMessage("Archivo: {0}.dbf Eliminado".format(self.table.name))
            lyer = mapping.Layer('CATALOGO_CENFEMUL_{0}.shp'.format(self.fech.strftime('%b%y').upper()))
            est_cenf.mapping_file(self,lyer)
            del lyer,sr
        return

    def copy2ps(self):
        # Copiando tablas a "Programas sociales"
        chdir(self.current)
        SetProgressorLabel('Copiando Tablas a PROGRAMAS_SOCIALES..')
        for filec in listdir(self.current):
            if ('REGISTRO' in filec or 'TABLA' in filec) and filec.endswith('.dbf'):
                copy2(filec, join(self.current,'PROGRAMAS_SOCIALES',filec))
        del filec
        return

    def report(self):
        SetProgressorLabel(u"Creando reporte de registros actualizados..")
        chdir(self.current)
        with SearchCursor(self.tab_eqv,["FECHA_ACT","DESCGO_ACT"]) as sc:
            act = [row[1] for row in sc if row[0][:7] == self.fech.strftime('%Y-%m')]
        result = {dato:act.count(dato) for dato in list(set(act))}
        """reg_ant = mapping.TableView(parameters[11].valueAsText)
        mkdir(u'Temp')
        comp = []
        for cenf,i in zip([reg_ant,self.reg_act],[0,1]):
            Statistics_analysis(cenf,join(getcwd(),u'Temp',u'sum_des_{0}.dbf'.format(i)),[["DESCGO_ACT","COUNT"]],"DESCGO_ACT")
            with SearchCursor(join(getcwd(),u'Temp',u'sum_des_{0}.dbf'.format(i)),"*") as sc:
                comp.append({row[1]:row[3] for row in sc})
        result = {row:(comp[1][row]-comp[0][row]) for row in comp[1]}"""
        tot = len(act)
        with open('Reporte_{0}.txt'.format(self.fech.strftime('%b%y').upper()),'w') as txt:
            movs = [['de "Alta"\t',u'CREACI\xd3N DE LOCALIDAD'],['"Reactivada{0}"\t',u'REACTIVACI\xd3N DE LOCALIDAD'],['"Fusionada{0}"\t',u'FUSI\xd3N DE LOCALIDAD'],['"Conurbada{0}"\t',u'CONURBACI\xd3N DE LOCALIDAD'],['"Cambio de municipio"',u'LOCALIDAD QUE CAMBIA DE MUNICIPIO'],['"Cambia mun x creación"',u'LOCALIDAD QUE CAMBIA DE MUN. POR NUEVA CREACI\xd3N'],['"Cambio de entidad"',u'LOCALIDAD QUE CAMBIA DE ENTIDAD'],['"Desfusionada{0}"\t',u'DESFUSIONADA'],['"Desconurbada{0}"\t',u'DESCONURBADA'],['de "Baja"\t',u'BAJA DE LOCALIDAD POR SER SERVICIO',u'TAPIA O RUINAS',u'INEXISTENTE'],['"Cambio de nombre"',u'CAMBIO DE NOMBRE']]
            txt.write(u'Catálogo Único de Claves de Áreas Geoestadísticas Estatales, Municipales y Localidades, al mes de {0} ({1} localidades vigentes)\ncon un total de {2} registros actualizados, de los cuales fueron:\n\n'.format(self.fech.strftime('%B del %Y'),comas(self.nlocs),comas(tot)).encode('cp1254'))
            txt.write(u'\t {0}\n'.format('-'*47))
            for reg in movs:
                if reg[1] in [key for key in result]:
                    suma = result[reg[1]]
                    if reg[0] == 'de "Baja"\t':
                        suma += result[reg[2]]+result[reg[3]]
                    if suma != 0:
                        if suma == 1:
                            txt.write(u'\t|    1| Localidad\t{0}\t|\n'.format(reg[0].format('')).encode('cp1254'))
                        else:
                            txt.write(u'\t|{0}{1}| Localidades\t{2}\t|\n'.format(' '*(5-len(str(suma))),suma,reg[0].format('s')).encode('cp1254'))
                        if reg != movs[-1]:
                            txt.write(u'\t|{0}|{1}|\n'.format('-'*5,'-'*41))
            txt.write(u'\t {0}'.format('-'*47))
        return
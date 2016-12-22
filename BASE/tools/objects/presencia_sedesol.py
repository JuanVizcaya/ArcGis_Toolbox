# -*- coding: cp1252 -*-
from __future__ import unicode_literals, print_function, absolute_import
from arcpy import Parameter, mapping, AddField_management,SelectLayerByAttribute_management,CalculateField_management,TableToTable_conversion,ListFields,Frequency_analysis,DeleteField_management,FieldMappings, env
from arcpy.da import UpdateCursor
from os import chdir,startfile
from os.path import dirname, abspath
from itertools import izip
from .equivalencias import calc_equiv
from .utils import today
from .dbfpy.dbf import Dbf
from xlrd import open_workbook
from xlwt import easyxf
from xlutils.copy import copy
from sys import path

path.append(dirname(abspath(__file__)))

__all__ = ["pre_s"]

class pre_s(calc_equiv):
    def __init__(self):
        calc_equiv.__init__(self)
        self.fields = [["CVE_ACT","TEXT",0,0,9],["CVEMUNCACT","TEXT",0,0,5],["CVEENT_ACT","TEXT",0,0,2]]
        env.overwriteOutput = True
        self.cve_ent = [str(i).zfill(2) for i in xrange(1,33)]
        self.flm = FieldMappings()
        self.today = today()
        self.prog = {u'S052':u"LIC", u'0263':u"POP", u'S057':u"FONAR", u'S061':u"3X1", u'S065':u"PAJA", u'S071':u"PET", u'S072':u"OPO", u'S174':u"PEI", u'S176':u"PUAM", u'S216':u"PDZP", u'S241':u"SEVIJE", u'0170':u"COM", u'E003':u"INAPAM", u'0196':u"IMJUVE", u'0377':u"EASC", u'0197':u"IMJUV1", u'0263':u"LICV1", u'S017':u"FOMES", u'0342':u'VAQM'}
        env.overwriteOutput = True

    @property
    def parameters(self):
        table = Parameter('input_tab',u'Tabla vu_hapr_presxloc_final'.encode("cp1254"),"Input","GPTableView","Required")
        xls = Parameter('input_xls','Documento de Excel 97-2003',"Input",'DEFile','Required')
        xls.filter.list = ['xls']
        form = Parameter("input_bool","Conservar formato de origen","Input","GPBoolean","Optional")
        output = Parameter("output_name","Nombre del archivo de salida","Input","String","Required")
        cat_list = Parameter('input_cat',u'Catálogos disponibles'.encode("cp1254"),"Input",'String','Required')
        return [table,xls,form,output,cat_list]

    def check_extension(self,parameter):
        if parameter.altered:
            if not parameter.value.endswith('.xls'):
                parameter.value += '.xls'

    def set_workspace(self,tab,messages):
        self.mxd = mapping.MapDocument("CURRENT")
        tab = mapping.ListTableViews(self.mxd,tab,self.mxd.activeDataFrame)[0]
        env.workspace = tab.workspacePath
        chdir(env.workspace)

    def add_fields(self,tab,messages):
        for fld in self.fields:
    		AddField_management(tab,*fld)

    def fill(self,tab,messages):
        tab = mapping.ListTableViews(self.mxd,tab,self.mxd.activeDataFrame)[0]
        #arcpy.env.workspace = tab.workspacePath
        #os.chdir(arcpy.env.workspace)
    	SelectLayerByAttribute_management(tab,"NEW_SELECTION",""""CVE_ACT" <> '' AND "CVE_ACT" <> 'B'""")
    	CalculateField_management(tab,"CVEMUNCACT","!CVE_ACT!","PYTHON")
    	SelectLayerByAttribute_management(tab,"SWITCH_SELECTION")
    	cve_mun = [row[:5] for row in self.cve_loc]
    	setmun = set(cve_mun)
    	self.cve_mun = list(setmun)
    	del cve_mun, setmun
    	with UpdateCursor(tab,["CVE_MUN","CVEMUNCACT"]) as uc:
    		for row in uc:
    			if row[0] in self.cve_mun:
    				row[1] = row[0]
    				uc.updateRow(row)
        SelectLayerByAttribute_management(tab,"NEW_SELECTION",""""CVEMUNCACT" <> ''""")
        CalculateField_management(tab,"CVEENT_ACT","!CVEMUNCACT!","PYTHON")
        SelectLayerByAttribute_management(tab,"SWITCH_SELECTION")
        with UpdateCursor(tab,["CVE_EDO","CVEENT_ACT"]) as uc:
            for row in uc:
                if row[0] in self.cve_ent:
                    row[1] = row[0]
                    uc.updateRow(row)
        SelectLayerByAttribute_management(tab,"CLEAR_SELECTION")
        self.flm.loadFromString(u'CVEENT_ORI "CVEENT_ORI" true true false 2 Text 0 0 ,First,#,{0},CVE_EDO,-1,-1;CVEMUNCORI "CVEMUNCORI" true true false 5 Text 0 0 ,First,#,{0},CVE_MUN,-1,-1;CVELOCCORI "CVELOCCORI" true true false 9 Text 0 0 ,First,#,{0},CVE_LOC,-1,-1;CVEENT_ACT "CVEENT_ACT" true true false 2 Text 0 0 ,First,#,{0},CVEENT_ACT,-1,-1;CVEMUNCACT "CVEMUNCACT" true true false 5 Text 0 0 ,First,#,{0},CVEMUNCACT,-1,-1;CVELOCCACT "CVELOCCACT" true true false 9 Text 0 0 ,First,#,{0},CVE_ACT,-1,-1;FAM_LIC "FAM_LIC" true true false 6 Long 0 6 ,First,#,{0},F_S052,-1,-1;FAM_POP "FAM_POP" true true false 6 Long 0 6 ,First,#,{0},F_0263,-1,-1;FAM_FONAR "FAM_FONAR" true true false 6 Long 0 6 ,First,#,{0},F_S057,-1,-1;FAM_PDZP "FAM_PDZP" true true false 6 Long 0 6 ,First,#,{0},F_S216,-1,-1;FAM_3X1 "FAM_3X1" true true false 6 Long 0 6 ,First,#,{0},F_S061,-1,-1;FAM_PAJA "FAM_PAJA" true true false 6 Long 0 6 ,First,#,{0},F_S065,-1,-1;FAM_PET "FAM_PET" true true false 6 Long 0 6 ,First,#,{0},F_S071,-1,-1;FAM_OPO "FAM_OPO" true true false 6 Long 0 6 ,First,#,{0},F_S072,-1,-1;TIT_PEI "TIT_PEI" true true false 6 Long 0 6 ,First,#,{0},F_S174,-1,-1;FAM_PUAM "FAM_PUAM" true true false 6 Long 0 6 ,First,#,{0},F_S176,-1,-1;FAM_COM "FAM_COM" true true false 6 Long 0 6 ,First,#,{0},F_0170,-1,-1;FAM_INAPAM "FAM_INAPAM" true true false 6 Long 0 6 ,First,#,{0},F_E003,-1,-1;FAM_IMJUVE "FAM_IMJUVE" true true false 6 Long 0 6 ,First,#,{0},F_0196,-1,-1;FAM_SEVIJE "FAM_SEVIJE" true true false 6 Long 0 6 ,First,#,{0},F_S241,-1,-1;FAM_EASC "FAM_EASC" true true false 6 Long 0 6 ,First,#,{0},F_0377,-1,-1;FAM_IMJUV1 "FAM_IMJUV1" true true false 6 Long 0 6 ,First,#,{0},F_0197,-1,-1;FAM_LICV1 "FAM_LICV1" true true false 6 Long 0 6 ,First,#,{0},F_0263,-1,-1;FAM_FOMES "FAM_FOMES" true true false 6 Long 0 6 ,First,#,{0},F_S017,-1,-1;FAM_VAQM "FAM_VAQM" true true false 6 Long 0 6 ,First,#,{0},F_0342,-1,-1;BEN_LIC "BEN_LIC" true true false 6 Long 0 6 ,First,#,{0},B_S052,-1,-1;BEN_POP "BEN_POP" true true false 6 Long 0 6 ,First,#,{0},B_0263,-1,-1;BEN_FONAR "BEN_FONAR" true true false 6 Long 0 6 ,First,#,{0},B_S057,-1,-1;BEN_PDZP "BEN_PDZP" true true false 6 Long 0 6 ,First,#,{0},B_S216,-1,-1;BEN_3X1 "BEN_3X1" true true false 6 Long 0 6 ,First,#,{0},B_S061,-1,-1;BEN_PAJA "BEN_PAJA" true true false 6 Long 0 6 ,First,#,{0},B_S065,-1,-1;BEN_PET "BEN_PET" true true false 6 Long 0 6 ,First,#,{0},B_S071,-1,-1;BEN_OPO "BEN_OPO" true true false 6 Long 0 6 ,First,#,{0},B_S072,-1,-1;BEN_PUAM "BEN_PUAM" true true false 6 Long 0 6 ,First,#,{0},B_S176,-1,-1;BEN_PEI "BEN_PEI" true true false 6 Long 0 6 ,First,#,{0},B_S174,-1,-1;BEN_COM "BEN_COM" true true false 6 Long 0 6 ,First,#,{0},B_0170,-1,-1;BEN_INAPAM "BEN_INAPAM" true true false 6 Long 0 6 ,First,#,{0},B_E003,-1,-1;BEN_IMJUVE "BEN_IMJUVE" true true false 6 Long 0 6 ,First,#,{0},B_0196,-1,-1;BEN_SEVIJE "BEN_SEVIJE" true true false 6 Long 0 6 ,First,#,{0},B_S241,-1,-1;BEN_EASC "BEN_EASC" true true false 6 Long 0 6 ,First,#,{0},B_0377,-1,-1;BEN_IMJUV1 "BEN_IMJUV1" true true false 6 Long 0 6 ,First,#,{0},B_0197,-1,-1;BEN_LICV1 "BEN_LICV1" true true false 6 Long 0 6 ,First,#,{0},B_0263,-1,-1;BEN_FOMES "BEN_FOMES" true true false 6 Long 0 6 ,First,#,{0},B_S017,-1,-1;BEN_VAQM "BEN_VAQM" true true false 6 Long 0 6 ,First,#,{0},B_0342,-1,-1;PRE_LIC "PRE_LIC" true true false 6 Long 0 6 ,First,#,{0},P_S052,-1,-1;PRE_POP "PRE_POP" true true false 6 Long 0 6 ,First,#,{0},P_0263,-1,-1;PRE_FONAR "PRE_FONAR" true true false 6 Long 0 6 ,First,#,{0},P_S057,-1,-1;PRE_PDZP "PRE_PDZP" true true false 6 Long 0 6 ,First,#,{0},P_S216,-1,-1;PRE_3X1 "PRE_3X1" true true false 6 Long 0 6 ,First,#,{0},P_S061,-1,-1;PRE_PAJA "PRE_PAJA" true true false 6 Long 0 6 ,First,#,{0},P_S065,-1,-1;PRE_PET "PRE_PET" true true false 6 Long 0 6 ,First,#,{0},P_S071,-1,-1;PRE_OPO "PRE_OPO" true true false 6 Long 0 6 ,First,#,{0},P_S072,-1,-1;PRE_PEI "PRE_PEI" true true false 6 Long 0 6 ,First,#,{0},P_S174,-1,-1;PRE_PUAM "PRE_PUAM" true true false 6 Long 0 6 ,First,#,{0},P_S176,-1,-1;PRE_COM "PRE_COM" true true false 6 Long 0 6 ,First,#,{0},P_0170,-1,-1;PRE_INAPAM "PRE_INAPAM" true true false 6 Long 0 6 ,First,#,{0},P_E003,-1,-1;PRE_IMJUVE "PRE_IMJUVE" true true false 6 Long 0 6 ,First,#,{0},P_0196,-1,-1;PRE_SEVIJE "PRE_SEVIJE" true true false 6 Long 0 6 ,First,#,{0},P_S241,-1,-1;PRE_EASC "PRE_EASC" true true false 6 Long 0 6 ,First,#,{0},P_0377,-1,-1;PRE_IMJUV1 "PRE_IMJUV1" true true false 6 Long 0 6 ,First,#,{0},P_0197,-1,-1;PRE_LICV1 "PRE_LICV1" true true false 6 Long 0 6 ,First,#,{0},P_0263,-1,-1;PRE_FOMES "PRE_FOMES" true true false 6 Long 0 6 ,First,#,{0},P_S017,-1,-1;PRE_VAQM "PRE_VAQM" true true false 6 Long 0 6 ,First,#,{0},P_0342,-1,-1;RESP_PEI "RESP_PEI" true true false 6 Long 0 6 ,First,#,{0},RESP_PEI,-1,-1'.format(tab.name))
        TableToTable_conversion(tab,env.workspace,'t_padrones_{0}.dbf'.format(self.today),None,self.flm)
        fields = [fld.name for fld in ListFields('t_padrones_{0}.dbf'.format(self.today),None,"Integer")]
        Frequency_analysis('t_padrones_{0}.dbf'.format(self.today),"agregadoxentidad.dbf","CVEENT_ACT",fields)
        DeleteField_management("agregadoxentidad.dbf","FREQUENCY")
        Frequency_analysis('t_padrones_{0}.dbf'.format(self.today),"agregadoxmunicipio.dbf","CVEMUNCACT",fields)
        DeleteField_management("agregadoxmunicipio.dbf","FREQUENCY")
        Frequency_analysis('t_padrones_{0}.dbf'.format(self.today),"agregadoxlocalidad.dbf","CVELOCCACT",fields)
        DeleteField_management("agregadoxlocalidad.dbf","FREQUENCY")

    def comp_values(self,xls,op,salida,messages):
        styy = easyxf('pattern: pattern solid, fore_colour yellow;')
        styg = easyxf('pattern: pattern solid, fore_colour green;')

        book = open_workbook(xls,formatting_info=op)
        wb = copy(book)

        for agre,sheet,field,col_index,cve_index,flag in izip(("agregadoxentidad.dbf","agregadoxmunicipio.dbf"),(0,1),("CVEENT_ACT","CVEMUNCACT"),(2,4),(1,2),(u"99",u"99999")):
            dbf = Dbf(agre,readOnly = True)
            sh = book.sheet_by_index(sheet)
            ws = wb.get_sheet(sheet)

            cve = [record[field] for record in dbf]

            for i in xrange(5,sh.nrows):
                sum_col = []
                for j in xrange(col_index,sh.ncols):
                    row = (sh.cell_value(i,cve_index),'')[sh.cell_value(i,cve_index) == flag]
                    col = sh.cell_value(3,j)
                    ant = (("BEN","FAM"),("TIT","RESP"))[col == u"S174"]
                    if row in cve or i == (sh.nrows-1):
                        for nom in ant:
                            try:
                                if i != (sh.nrows-1) and j != (sh.ncols-1):
                                    val = dbf[cve.index(row)]["{0}_{1}".format(nom,self.prog[col])]

                                elif i == (sh.nrows-1) and j != (sh.ncols-1):
                                    val = sum([record["{0}_{1}".format(nom,self.prog[col])] for record in dbf])

                                elif j == (sh.ncols-1):
                                    val = sum(sum_col)

                                if sh.cell_value(i,j) == val:
                                    ws.write(i,j,sh.cell_value(i,j),styg)
                                    sum_col.append(val)
                                    break
                                else:
                                    ws.write(i,j,sh.cell_value(i,j),styy)
                            except KeyError:
                                messages.AddMessage(col)
                    else:
                        continue
        wb.save(salida)
        startfile(salida)
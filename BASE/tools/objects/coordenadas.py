from __future__ import unicode_literals, print_function, absolute_import
from arcpy.mapping import MapDocument, ListLayers, ListTableViews, TableView, RemoveTableView, AddTableView, RemoveLayer
from arcpy.da import InsertCursor, SearchCursor
from arcpy import Parameter, FieldMappings, TableToTable_conversion, RefreshTOC, AddJoin_management, SelectLayerByAttribute_management, RemoveJoin_management, SpatialReference
from arcpy import PointGeometry, Point, AddField_management, CalculateField_management, env
from itertools import izip
from os import chdir, mkdir, getcwd

__all__ = ["obc"]

class obc(object):
    def __init__(self):
        self.__licens = "users"
        env.overwriteOutput = True

    @property
    def _license(self):
        return True

    @property
    def params(self):
        param0 = Parameter('input_cat','Catalogo CENFEMUL',"Input",'GPFeatureLayer','Required')
        param1 = Parameter('input_eqv','Tabla de Equivalencia',"Input",'GPTableView','Required')
        param2 = Parameter('input_uni','Universo mes anterior',"Input",'GPTableView','Required')
        return [param0,param1,param2]

    def execute(self, parameters, messages):
        mxd = MapDocument('current')
        lyr = ListLayers(mxd,parameters[0].valueAsText,mxd.activeDataFrame)[0]
        eqv = ListTableViews(mxd,parameters[1].valueAsText,mxd.activeDataFrame)[0]
        uni = ListTableViews(mxd,parameters[2].valueAsText,mxd.activeDataFrame)[0]
        messages.AddMessage(parameters[0].valueAsText)
        flm = FieldMappings()
        flm.loadFromString(u'CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;LNG_DG "LNG_DG" true true false 12 Double 8 12 ,First,#,{0},LON_DEC,-1,-1;LAT_DG "LAT_DG" true true false 10 Double 8 10 ,First,#,{0},LAT_DEC,-1,-1'.format(lyr.name))
        chdir(lyr.workspacePath)
        chdir('..')
        try:
            mkdir(u"{0}\\PROCESO_COORDENADAS".format(getcwd().decode("cp1254")))
        except  WindowsError:
            messages.AddMessage(u"{0}\\PROCESO_COORDENADAS".format(getcwd().decode("cp1254")))
        try:
            mkdir(u"{0}\\PROCESO_COORDENADAS\\FINAL".format(getcwd().decode("cp1254")))
        except  WindowsError:
            pass
        TableToTable_conversion(lyr,u"{0}\\PROCESO_COORDENADAS\\FINAL".format(getcwd().decode("cp1254")),"t_coord_actvigente_{0}{1}.dbf".format(lyr.name[-5:-2].lower(),int(lyr.name[-2:])+2000),None,flm)
        flm.removeAll()
        flm.loadFromString(u'CVE_LOCC "CVE_LOCC" true true false 9 Text 0 0 ,First,#,{0},CVE_LOCC,-1,-1;LAMBX "LAMBX" true true false 18 Double 5 18 ,First,#,{0},LAMBX,-1,-1;LAMBY "LAMBY" true true false 18 Double 5 18 ,First,#,{0},LAMBY,-1,-1;LONGI "LONGI" true true false 13 Double 8 13 ,First,#,{0},LONGI,-1,-1;LATI "LATI" true true false 13 Double 8 13 ,First,#,{0},LATI,-1,-1'.format(uni.name))
        TableToTable_conversion(uni,u"{0}\\PROCESO_COORDENADAS\\FINAL".format(getcwd().decode("cp1254")),"universo_{0}{1}.dbf".format(lyr.name[-5:-2].lower(),int(lyr.name[-2:])+2000),None,flm)
        act = TableView(u"{0}\\PROCESO_COORDENADAS\\FINAL\\t_coord_actvigente_{1}{2}.dbf".format(getcwd().decode("cp1254"),lyr.name[-5:-2].lower(),int(lyr.name[-2:])+2000))
        RemoveTableView(mxd.activeDataFrame,uni)
        uni = TableView(u"{0}\\PROCESO_COORDENADAS\\FINAL\\universo_{1}{2}.dbf".format(getcwd().decode("cp1254"),lyr.name[-5:-2].lower(),int(lyr.name[-2:])+2000))
        AddTableView(mxd.activeDataFrame,act)
        AddTableView(mxd.activeDataFrame,uni)
        RefreshTOC()
        AddJoin_management(act,"CVE_LOCC",uni,"CVE_LOCC")
        SelectLayerByAttribute_management(act,"NEW_SELECTION","\"{0}.CVE_LOCC\" IS NULL".format(uni.name))
        RemoveJoin_management(act)
        with InsertCursor(uni,[u'CVE_LOCC', u'LAMBX', u'LAMBY', u'LONGI', u'LATI']) as ic:
            sr = SpatialReference()
            sr.loadFromString(u"PROJCS['Lambert',GEOGCS['GCS_ITRF_1992',DATUM['D_ITRF_1992',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-102.0],PARAMETER['Standard_Parallel_1',17.5],PARAMETER['Standard_Parallel_2',29.5],PARAMETER['Scale_Factor',1.0],PARAMETER['Latitude_Of_Origin',12.0],UNIT['Meter',1.0]];-37031600 -25743800 113924041.206794;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision")
            with SearchCursor(act,[u'CVE_LOCC', u'LNG_DG', u'LAT_DG']) as sc:
                for row in sc:
                    pg = PointGeometry(Point(row[1],row[2]),SpatialReference("ITRF 1992")).projectAs(sr)
                    ic.insertRow((row[0],pg.labelPoint.X,pg.labelPoint.Y,row[1],row[2]))
        SelectLayerByAttribute_management(act,"CLEAR_SELECTION")
        flm.removeAll()
        flm.loadFromString(u'CVELOCCACT "CVELOCCACT" true true false 9 Text 0 0 ,First,#,{0},CVELOCCACT,-1,-1;CVELOCCORI "CVELOCCORI" true true false 9 Text 0 0 ,First,#,{0},CVELOCCORI,-1,-1'.format(eqv.name))
        TableToTable_conversion(eqv,u"{0}\\PROCESO_COORDENADAS\\FINAL".format(getcwd().decode("cp1254")),"t_coord_equival_{0}{1}.dbf".format(lyr.name[-5:-2].lower(),int(lyr.name[-2:])+2000),None,flm)
        RemoveTableView(mxd.activeDataFrame,eqv)
        eqv = TableView(u"{0}\\PROCESO_COORDENADAS\\FINAL\\t_coord_equival_{1}{2}.dbf".format(getcwd().decode("cp1254"),lyr.name[-5:-2].lower(),int(lyr.name[-2:])+2000))
        RemoveLayer(mxd.activeDataFrame,lyr)
        AddTableView(mxd.activeDataFrame,eqv)
        RefreshTOC()
        for fld_ops in [[u'LMX_ACT', u'DOUBLE', 18, 5, 18], [u'LMY_ACT', u'DOUBLE', 18, 5, 18], [u'LNG_ACT', u'DOUBLE', 13, 8, 13], [u'LAT_ACT', u'DOUBLE', 13, 8, 13], [u'LMX_ORIG', u'DOUBLE', 18, 5, 18], [u'LMY_ORIG', u'DOUBLE', 18, 5, 18], [u'LNG_ORIG', u'DOUBLE', 13, 8, 13], [u'LAT_ORIG', u'DOUBLE', 13, 8, 13]]:
            AddField_management(eqv,*fld_ops)
        AddJoin_management(eqv,u"CVELOCCACT",uni,"CVE_LOCC")
        SelectLayerByAttribute_management(eqv,"NEW_SELECTION","\"{0}.CVE_LOCC\" IS NOT NULL".format(uni.name))
        for fld, fld2 in izip([u'LMX_ACT',u'LMY_ACT',u'LNG_ACT',u'LAT_ACT'],[u'LAMBX',u'LAMBY',u'LONGI',u'LATI']):
            CalculateField_management(eqv,"{0}.{1}".format(eqv.name,fld),"!{0}.{1}!".format(uni.name,fld2),"PYTHON")
        RemoveJoin_management(eqv)
        SelectLayerByAttribute_management(eqv,"CLEAR_SELECTION")
        AddJoin_management(eqv,u"CVELOCCORI",uni,"CVE_LOCC")
        SelectLayerByAttribute_management(eqv,"NEW_SELECTION","\"{0}.CVE_LOCC\" IS NOT NULL".format(uni.name))
        for fld, fld2 in izip([u'LMX_ORIG',u'LMY_ORIG',u'LNG_ORIG',u'LAT_ORIG'],[u'LAMBX',u'LAMBY',u'LONGI',u'LATI']):
            CalculateField_management(eqv,"{0}.{1}".format(eqv.name,fld),"!{0}.{1}!".format(uni.name,fld2),"PYTHON")
        RemoveJoin_management(eqv)
        SelectLayerByAttribute_management(eqv,"CLEAR_SELECTION")
        return
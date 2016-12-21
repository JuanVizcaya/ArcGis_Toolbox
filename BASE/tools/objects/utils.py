from __future__ import unicode_literals, print_function, absolute_import
from arcpy import ListFields, CreateTable_management, DeleteField_management, AddField_management, mapping, RefreshTOC
from arcpy.da import SearchCursor
from collections import OrderedDict
from datetime import datetime as dt
from zipfile import ZipFile, ZIP_DEFLATED
from os.path import dirname, exists
from os import mkdir, getcwd
from urllib import urlretrieve, urlopen
from re import compile, IGNORECASE
try:
    import cPickle as pickle
except ImportError:
    import pickle
import locale

locale.setlocale(locale.LC_ALL, '')
__mth = {'01':u"ENERO",'02':u"FEBRERO",'03':u"MARZO",'04':u"ABRIL",'05':u"MAYO",'06':u"JUNIO",'07':u"JULIO",'08':u"AGOSTO",'09':u"SEPTIEMBRE",'10':u"OCTUBRE",'11':u"NOVIEMBRE",'12':u"DICIEMBRE"}

__mth_list = [__mth[str(i).zfill(2)][:3] for i in xrange(1,13)]

def change(var):
    return dt.strptime(var.lower(),"%b%y").strftime("%Y%m")

def change_format(fch):
    return dt.strptime(fch,"%Y-%m-%d").strftime("%d/%m/%Y")

def checkdate(lst):
    lst.sort(reverse = True)
    d = OrderedDict()
    for value in lst:
        d[dt.strptime(value,'%Y%m.catz').strftime('%Y %B').upper()] = value
    return d

def download(url,path):
    urlretrieve(url,path)

def matching(foo,bar):
    return bool(compile(foo, IGNORECASE).match(bar))

def mth_ant(mes):
    return __mth_list[__mth_list.index(mes)-1]

def myzip(path,name,data):
    with ZipFile(path, 'w', ZIP_DEFLATED) as zf:
        zf.writestr(name, pickle.dumps(data,pickle.HIGHEST_PROTOCOL))

def readFromStr(url):
    return pickle.loads(urlopen(url).read())

def today():
    return dt.today().strftime("%d%b%y")

def unzip(path):
    with ZipFile(path,'r') as zf:
        zf.extractall(dirname(path))

def writeFromObj(path,data):
    with open(path,'wb') as op:
        pickle.dump(data)

def readFromObj(path):
    with open(path,'rb') as op:
        lst = pickle.load(op)
    return lst

def mkd(path):
    if not exists(path):
        mkdir(path)

def mklistdir(lst):
    for pth in lst:
        mkd(pth)

def comas(i):
    return locale.format("%i",i, grouping=True)

def mktable(name,fields):
    CreateTable_management(getcwd(),name)
    tab = mapping.TableView(name)
    for fld in fields:
        AddField_management(tab,*fld)
    DeleteField_management(tab,'Field1')
    return tab

def read_dbf(tab_dir,field_ord): #lee un dbf y lo ordena segun el nombre del campo deseado
        fields = [fld.name for fld in ListFields(tab_dir)]
        tab = mapping.TableView(tab_dir)
        with SearchCursor(tab,fields) as sc:
            rows = [row for row in sc]
        n = fields.index(field_ord)
        rows.sort(key=lambda row: row[n])
        return rows

def map_file(filec):
    nom = filec.split('\\')[-1].split('.')[0]
    mxd = mapping.MapDocument("CURRENT")
    df = mapping.ListDataFrames(mxd, "*")[0]
    if not nom in [dat.name for dat in df]:
        if filec.endswith('.dbf'):
            tab = mapping.TableView(filec)
            mapping.AddTableView(df,tab)
        elif filec.endswith('.shp'):
            lyr = mapping.Layer(filec)
            mapping.AddLayer(df,lyr)
        RefreshTOC()
        return nom
    else:
        return filec
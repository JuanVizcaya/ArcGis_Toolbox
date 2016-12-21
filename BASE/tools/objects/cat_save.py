from __future__ import unicode_literals, print_function, absolute_import
from arcpy.da import SearchCursor
from arcpy import Parameter, Exists, ListFields
from os.path import join
from .utils import change, myzip
from .data import bar

__all__ = ["act_equiv"]

class act_equiv(object):
    def __init__(self):
        self.__path = bar.fpath
        self.__licens = "users"

    @property
    def _license(self):
        #return utils.license_v2(utils.licens.lists[self.__licens])
        return True
    
    @property
    def params(self):
        layer = Parameter('input_lay',u'Cat\xe1logo CENFEMUL',"Input","GPTableView","Required")
        table = Parameter('input_tab',u'Tabla con claves geostad\xedsticas',"Input","GPTableView","Required")    
        return [layer,table]
        
    def actualiza(self,parameters,messages):
        self.ops = bar.cats
        if "{0}.catz".format(change(parameters[0][-5:])) not in self.ops:
            with SearchCursor(parameters[0],["CVE_LOCC"]) as sc:
                self.cve_loc = [row[0] for row in sc]
            with SearchCursor(parameters[1],["CVELOCCACT","CVELOCCORI","DESCGO_ACT","FECHA_ACT"]) as sc:
                self.cve_eqv = [row for row in sc]
        
            myzip(join(self.__path,"{0}.catz".format(change(parameters[0][-5:]))),"cdata.cat",self.cve_loc)
            myzip(join(self.__path,"A0EQV01.eqvz"),"edata.eqv",self.cve_eqv)
        return
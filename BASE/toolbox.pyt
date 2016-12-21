from __future__ import unicode_literals, print_function, absolute_import
from tools import *

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "DGAAE"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [EQV, ACT_EQV, Estand_CENF, COORD, CAT_LOC, SIIPSO, Sepo, Dispos, Archs_DM, AyB_DM, LICONSA, DICONSA, Estancias, Comedores, PUB, Pre_SEDESOL]
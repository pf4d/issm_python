from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class amr(object):
    """
    AMR Class definition

    Usage:
        amr=amr();
    """

    def __init__(self): # {{{
        self.level_max        = 0.
        self.region_level_1   = 0.
        self.region_level_max = 0.

        #set defaults
        self.setdefaultparameters()
    #}}}
    def __repr__(self): # {{{
        string="   amr parameters:"
        string="%s\n%s"%(string,fielddisplay(self,"level_max","maximum refinement level (1, 2, 3 or 4)"))
        string="%s\n%s"%(string,fielddisplay(self,"region_level_1","region which will be refined once (level 1) [ m ]"))
        string="%s\n%s"%(string,fielddisplay(self,"region_level_max","region which will be refined with level_max [ m ]"))
        return string
    #}}}
    def setdefaultparameters(self): # {{{

        #level_max: 2 to 4
        self.level_max=2

        #region_level_1: region around (m) the discontinuity (grounding line or ice front) where the mesh will be refined once (h=1).
        self.region_level_1=20000.

        #region_level_max: region around (m) the discontinuity (grounding line or ice front) where the mesh will be refined with max level of refinement (h=level_max).
        self.region_level_max=15000.

        return self
        #}}}
    def checkconsistency(self,md,solution,analyses):    # {{{
        md = checkfield(md,'fieldname','amr.level_max','numel',[1],'>=',0,'<=',4)
        md = checkfield(md,'fieldname','amr.region_level_1','numel',[1],'>',0,'NaN',1,'Inf',1)
        md = checkfield(md,'fieldname','amr.region_level_max','numel',[1],'>',0,'NaN',1,'Inf',1)
                #it was adopted 20% of the region_level_1
        if self.region_level_1-self.region_level_max<0.2*self.region_level_1:
            md.checkmessage("region_level_max should be lower than 80% of region_level_1")

        return md
    # }}}
    def marshall(self,prefix,md,fid):    # {{{
        WriteData(fid,prefix,'object',self,'fieldname','level_max','format','Integer')
        WriteData(fid,prefix,'object',self,'fieldname','region_level_1','format','Double')
        WriteData(fid,prefix,'object',self,'fieldname','region_level_max','format','Double')
    # }}}

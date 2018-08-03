from issm.fielddisplay import fielddisplay
from issm.project3d import project3d
from issm.checkfield import checkfield
from issm.WriteData import WriteData
import numpy as np

class mismipbasalforcings(object):
    """ 
    MISMIP Basal Forcings class definition

        Usage:
	    mismipbasalforcings=mismipbasalforcings()
    """

    def __init__(self): # {{{

        self.groundedice_melting_rate = float('NaN')
        self.meltrate_factor = float('NaN')
        self.threshold_thickness = float('NaN')
        self.upperdepth_melt = float('NaN')
        self.geothermalflux = float('NaN')

	self.setdefaultparameters()

    #}}}
    def __repr__(self): # {{{
        string=" MISMIP+ basal melt parameterization\n"
        string="%s\n%s"%(string,fielddisplay(self,"groundedice_melting_rate","basal melting rate (positive if melting) [m/yr]"))
        string="%s\n%s"%(string,fielddisplay(self,"meltrate_factor","Melt-rate rate factor [1/yr] (sign is opposite to MISMIP+ benchmark to remain consistent with ISSM convention of positive values for melting)"))
        string="%s\n%s"%(string,fielddisplay(self,"threshold_thickness","Threshold thickness for saturation of basal melting [m]"))
        string="%s\n%s"%(string,fielddisplay(self,"upperdepth_melt","Depth above which melt rate is zero [m]"))
        string="%s\n%s"%(string,fielddisplay(self,"geothermalflux","Geothermal heat flux [W/m^2]"))
	return string
    #}}}
    def extrude(self,md): # {{{
        self.groundedice_melting_rate=project3d(md,'vector',self.groundedice_melting_rate,'type','node','layer',1)
        self.geothermalflux=project3d(md,'vector',self.geothermalflux,'type','node','layer',1)    #bedrock only gets geothermal flux
	return self
    #}}}
    def initialize(self,md): # {{{
        if np.all(np.isnan(self.groundedice_melting_rate)):
            self.groundedice_melting_rate=np.zeros(md.mesh.numberofvertices)
            print ' no basalforcings.groundedice_melting_rate specified: values set as zero'
        return self
    #}}}
    def setdefaultparameters(self): # {{{
        # default values for melting parameterization
        self.meltrate_factor = 0.2
        self.threshold_thickness = 75.
        self.upperdepth_melt = -100.
	return self
    #}}}
    def checkconsistency(self,md,solution,analyses):    # {{{

	#Early return
        if 'MasstransportAnalysis' in analyses and not (solution=='TransientSolution' and md.transient.ismasstransport==0):

	    md = checkfield(md,'fieldname','basalforcings.groundedice_melting_rate','NaN',1,'Inf',1,'timeseries',1)
	    md = checkfield(md,'fieldname','basalforcings.meltrate_factor','>=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.threshold_thickness','>=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.upperdepth_melt','<=',0,'numel',[1])

        if 'BalancethicknessAnalysis' in analyses:

	    md = checkfield(md,'fieldname','basalforcings.groundedice_melting_rate','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
	    md = checkfield(md,'fieldname','basalforcings.meltrate_factor','>=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.threshold_thickness','>=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.upperdepth_melt','<=',0,'numel',[1])

        if 'ThermalAnalysis' in analyses and not (solution=='TransientSolution' and md.transient.isthermal==0):

	    md = checkfield(md,'fieldname','basalforcings.groundedice_melting_rate','NaN',1,'Inf',1,'timeseries',1)
	    md = checkfield(md,'fieldname','basalforcings.meltrate_factor','>=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.threshold_thickness','>=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.upperdepth_melt','<=',0,'numel',[1])
	    md = checkfield(md,'fieldname','basalforcings.geothermalflux','NaN',1,'Inf',1,'timeseries',1,'>=',0)
	return md
    # }}}
    def marshall(self,prefix,md,fid):    # {{{

        yts=md.constants.yts
        if yts!=365.2422*24.*3600.:
            print 'WARNING: value of yts for MISMIP+ runs different from ISSM default!'

        floatingice_melting_rate = np.zeros((md.mesh.numberofvertices))
        floatingice_melting_rate = md.basalforcings.meltrate_factor*np.tanh((md.geometry.base-md.geometry.bed)/md.basalforcings.threshold_thickness)*np.amax(md.basalforcings.upperdepth_melt-md.geometry.base,0)

	WriteData(fid,prefix,'name','md.basalforcings.model','data',3,'format','Integer')
	WriteData(fid,prefix,'data',floatingice_melting_rate,'format','DoubleMat','name','md.basalforcings.floatingice_melting_rate','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
	WriteData(fid,prefix,'object',self,'fieldname','groundedice_melting_rate','format','DoubleMat','name','md.basalforcings.groundedice_melting_rate','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
	WriteData(fid,prefix,'object',self,'fieldname','geothermalflux','name','md.basalforcings.geothermalflux','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
	WriteData(fid,prefix,'object',self,'fieldname','meltrate_factor','format','Double','scale',1./yts)
	WriteData(fid,prefix,'object',self,'fieldname','threshold_thickness','format','Double')
	WriteData(fid,prefix,'object',self,'fieldname','upperdepth_melt','format','Double')

    # }}}

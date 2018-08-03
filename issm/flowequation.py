import numpy as np
import copy
from issm.project3d import project3d
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData
import issm.MatlabFuncs as m

class flowequation(object):
	"""
	FLOWEQUATION class definition

	   Usage:
	      flowequation=flowequation();
	"""

	def __init__(self): # {{{
		
		self.isSIA                          = 0
		self.isSSA                          = 0
		self.isL1L2                         = 0
		self.isHO                           = 0
		self.isFS                           = 0
		self.fe_SSA                         = ''
		self.fe_HO                          = ''
		self.fe_FS                          = ''
		self.augmented_lagrangian_r         = 1.
		self.augmented_lagrangian_rhop      = 1.
		self.augmented_lagrangian_rlambda   = 1.
		self.augmented_lagrangian_rholambda = 1.
		self.XTH_theta                      = 0.
		self.vertex_equation                = float('NaN')
		self.element_equation               = float('NaN')
		self.borderSSA                      = float('NaN')
		self.borderHO                       = float('NaN')
		self.borderFS                       = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   flow equation parameters:'

		string="%s\n%s"%(string,fielddisplay(self,'isSIA',"is the Shallow Ice Approximation (SIA) used ?"))
		string="%s\n%s"%(string,fielddisplay(self,'isSSA',"is the Shelfy-Stream Approximation (SSA) used ?"))
		string="%s\n%s"%(string,fielddisplay(self,'isL1L2',"are L1L2 equations used ?"))
		string="%s\n%s"%(string,fielddisplay(self,'isHO',"is the Higher-Order (HO) approximation used ?"))
		string="%s\n%s"%(string,fielddisplay(self,'isFS',"are the Full-FS (FS) equations used ?"))
		string="%s\n%s"%(string,fielddisplay(self,'fe_SSA',"Finite Element for SSA: 'P1', 'P1bubble' 'P1bubblecondensed' 'P2'"))
		string="%s\n%s"%(string,fielddisplay(self,'fe_HO' ,"Finite Element for HO:  'P1' 'P1bubble' 'P1bubblecondensed' 'P1xP2' 'P2xP1' 'P2'"))
		string="%s\n%s"%(string,fielddisplay(self,'fe_FS' ,"Finite Element for FS:  'P1P1' (debugging only) 'P1P1GLS' 'MINIcondensed' 'MINI' 'TaylorHood' 'LATaylorHood' 'XTaylorHood'"))
		string="%s\n%s"%(string,fielddisplay(self,'vertex_equation',"flow equation for each vertex"))
		string="%s\n%s"%(string,fielddisplay(self,'element_equation',"flow equation for each element"))
		string="%s\n%s"%(string,fielddisplay(self,'borderSSA',"vertices on SSA's border (for tiling)"))
		string="%s\n%s"%(string,fielddisplay(self,'borderHO',"vertices on HO's border (for tiling)"))
		string="%s\n%s"%(string,fielddisplay(self,'borderFS',"vertices on FS' border (for tiling)"))
		return string
		#}}}
	def extrude(self,md): # {{{
		self.element_equation=project3d(md,'vector',self.element_equation,'type','element')
		self.vertex_equation=project3d(md,'vector',self.vertex_equation,'type','node')
		self.borderSSA=project3d(md,'vector',self.borderSSA,'type','node')
		self.borderHO=project3d(md,'vector',self.borderHO,'type','node')
		self.borderFS=project3d(md,'vector',self.borderFS,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{

		#P1 for SSA
		self.fe_SSA= 'P1';

		#P1 for HO
		self.fe_HO= 'P1';

		#MINI condensed element for FS by default
		self.fe_FS = 'MINIcondensed';

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if ('StressbalanceAnalysis' not in analyses and 'StressbalanceSIAAnalysis' not in analyses) or (solution=='TransientSolution' and not md.transient.isstressbalance):
			return md

		md = checkfield(md,'fieldname','flowequation.isSIA','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.isSSA','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.isL1L2','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.isHO','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.isFS','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.fe_SSA','values',['P1','P1bubble','P1bubblecondensed','P2','P2bubble'])
		md = checkfield(md,'fieldname','flowequation.fe_HO' ,'values',['P1','P1bubble','P1bubblecondensed','P1xP2','P2xP1','P2','P2bubble','P1xP3','P2xP4'])
		md = checkfield(md,'fieldname','flowequation.fe_FS' ,'values',['P1P1','P1P1GLS','MINIcondensed','MINI','TaylorHood','XTaylorHood','OneLayerP4z','CrouzeixRaviart'])
		md = checkfield(md,'fieldname','flowequation.borderSSA','size',[md.mesh.numberofvertices],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.borderHO','size',[md.mesh.numberofvertices],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.borderFS','size',[md.mesh.numberofvertices],'values',[0,1])
		md = checkfield(md,'fieldname','flowequation.augmented_lagrangian_r','numel',[1],'>',0.)
		md = checkfield(md,'fieldname','flowequation.augmented_lagrangian_rhop','numel',[1],'>',0.)
		md = checkfield(md,'fieldname','flowequation.augmented_lagrangian_rlambda','numel',[1],'>',0.)
		md = checkfield(md,'fieldname','flowequation.augmented_lagrangian_rholambda','numel',[1],'>',0.)
		md = checkfield(md,'fieldname','flowequation.XTH_theta','numel',[1],'>=',0.,'<',.5)
		if m.strcmp(md.mesh.domaintype(),'2Dhorizontal'):
			md = checkfield(md,'fieldname','flowequation.vertex_equation','size',[md.mesh.numberofvertices],'values',[1,2])
			md = checkfield(md,'fieldname','flowequation.element_equation','size',[md.mesh.numberofelements],'values',[1,2])
		elif m.strcmp(md.mesh.domaintype(),'3D'):
			md = checkfield(md,'fieldname','flowequation.vertex_equation','size',[md.mesh.numberofvertices],'values',np.arange(0,8+1))
			md = checkfield(md,'fieldname','flowequation.element_equation','size',[md.mesh.numberofelements],'values',np.arange(0,8+1))
		else:
			raise RuntimeError('mesh type not supported yet')
		if not (self.isSIA or self.isSSA or self.isL1L2 or self.isHO or self.isFS):
			md.checkmessage("no element types set for this model")

		if 'StressbalanceSIAAnalysis' in analyses:
			if any(self.element_equation==1):
				if np.any(np.logical_and(self.vertex_equation,md.mask.groundedice_levelset)):
					print "\n !!! Warning: SIA's model is not consistent on ice shelves !!!\n"

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','isSIA','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isSSA','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isL1L2','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isHO','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isFS','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','fe_SSA','data',self.fe_SSA,'format','String')
		WriteData(fid,prefix,'object',self,'fieldname','fe_HO','data',self.fe_HO,'format','String')
		WriteData(fid,prefix,'object',self,'fieldname','fe_FS','data',self.fe_FS ,'format','String')
		WriteData(fid,prefix,'object',self,'fieldname','augmented_lagrangian_r','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','augmented_lagrangian_rhop','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','augmented_lagrangian_rlambda','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','augmented_lagrangian_rholambda','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','XTH_theta','data',self.XTH_theta ,'format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','borderSSA','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','borderHO','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','borderFS','format','DoubleMat','mattype',1)
		#convert approximations to enums
		WriteData(fid,prefix,'data',self.vertex_equation,'name','md.flowequation.vertex_equation','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'data',self.element_equation,'name','md.flowequation.element_equation','format','DoubleMat','mattype',2)

	# }}}

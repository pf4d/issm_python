from issm.fielddisplay import fielddisplay
from issm.project3d import project3d
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class masstransport(object):
	"""
	MASSTRANSPORT class definition

	   Usage:
	      masstransport=masstransport();
	"""

	def __init__(self): # {{{
		self.spcthickness           = float('NaN')
		self.isfreesurface          = 0
		self.min_thickness          = 0.
		self.hydrostatic_adjustment = 0
		self.stabilization          = 0
		self.vertex_pairing         = float('NaN')
		self.penalty_factor         = 0
		self.requested_outputs      = []

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   Masstransport solution parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'spcthickness','thickness constraints (NaN means no constraint) [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'isfreesurface','do we use free surfaces (FS only) are mass conservation'))
		string="%s\n%s"%(string,fielddisplay(self,'min_thickness','minimum ice thickness allowed [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'hydrostatic_adjustment','adjustment of ice shelves surface and bed elevations: ''Incremental'' or ''Absolute'' '))
		string="%s\n%s"%(string,fielddisplay(self,'stabilization','0: no, 1: artificial_diffusivity, 2: streamline upwinding, 3: discontinuous Galerkin, 4: Flux Correction Transport'))
		string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','additional outputs requested'))

		return string
		#}}}
	def extrude(self,md): # {{{
		self.spcthickness=project3d(md,'vector',self.spcthickness,'type','node')
		return self
	#}}}
	def defaultoutputs(self,md): # {{{

		return ['Thickness','Surface','Base']

	#}}}
	def setdefaultparameters(self): # {{{

		#Type of stabilization to use 0:nothing 1:artificial_diffusivity 3:Discontinuous Galerkin
		self.stabilization=1

		#Factor applied to compute the penalties kappa=max(stiffness matrix)*10^penalty_factor
		self.penalty_factor=3

		#Minimum ice thickness that can be used
		self.min_thickness=1

		#Hydrostatic adjustment
		self.hydrostatic_adjustment='Absolute'

		#default output
		self.requested_outputs=['default']
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if ('MasstransportAnalysis' not in analyses) or (solution=='TransientSolution' and not md.transient.ismasstransport):
			return md

		md = checkfield(md,'fieldname','masstransport.spcthickness','Inf',1,'timeseries',1)
		md = checkfield(md,'fieldname','masstransport.isfreesurface','values',[0,1])
		md = checkfield(md,'fieldname','masstransport.hydrostatic_adjustment','values',['Absolute','Incremental'])
		md = checkfield(md,'fieldname','masstransport.stabilization','values',[0,1,2,3,4])
		md = checkfield(md,'fieldname','masstransport.min_thickness','>',0)
		md = checkfield(md,'fieldname','masstransport.requested_outputs','stringrow',1)

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'object',self,'fieldname','spcthickness','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'fieldname','isfreesurface','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','min_thickness','format','Double')
		WriteData(fid,prefix,'data',self.hydrostatic_adjustment,'format','String','name','md.masstransport.hydrostatic_adjustment')
		WriteData(fid,prefix,'object',self,'fieldname','stabilization','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','vertex_pairing','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'fieldname','penalty_factor','format','Double')

		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.masstransport.requested_outputs','format','StringArray')
	# }}}

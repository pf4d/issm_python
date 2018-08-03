import numpy as np
import sys
import copy
from project3d import project3d
from fielddisplay import fielddisplay
from checkfield import checkfield
from WriteData import WriteData
import MatlabFuncs as m

class stressbalance(object):
	"""
	STRESSBALANCE class definition

	   Usage:
	      stressbalance=stressbalance();
	"""

	def __init__(self): # {{{
		self.spcvx                    = float('NaN')
		self.spcvy                    = float('NaN')
		self.spcvz                    = float('NaN')
		self.restol                   = 0
		self.reltol                   = 0
		self.abstol                   = 0
		self.isnewton                 = 0
		self.FSreconditioning     = 0
		self.viscosity_overshoot      = 0
		self.icefront                 = float('NaN')
		self.maxiter                  = 0
		self.shelf_dampening          = 0
		self.vertex_pairing           = float('NaN')
		self.penalty_factor           = float('NaN')
		self.rift_penalty_lock        = float('NaN')
		self.rift_penalty_threshold   = 0
		self.referential              = float('NaN')
		self.loadingforce             = float('NaN')
		self.requested_outputs        = []

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		
		string='   StressBalance solution parameters:'
		string="%s\n%s"%(string,'      Convergence criteria:')
		string="%s\n%s"%(string,fielddisplay(self,'restol','mechanical equilibrium residual convergence criterion'))
		string="%s\n%s"%(string,fielddisplay(self,'reltol','velocity relative convergence criterion, NaN: not applied'))
		string="%s\n%s"%(string,fielddisplay(self,'abstol','velocity absolute convergence criterion, NaN: not applied'))
		string="%s\n%s"%(string,fielddisplay(self,'isnewton',"0: Picard's fixed point, 1: Newton's method, 2: hybrid"))
		string="%s\n%s"%(string,fielddisplay(self,'maxiter','maximum number of nonlinear iterations'))
		string="%s\n%s"%(string,fielddisplay(self,'viscosity_overshoot','over-shooting constant new=new+C*(new-old)'))

		string="%s\n%s"%(string,'\n      boundary conditions:')
		string="%s\n%s"%(string,fielddisplay(self,'spcvx','x-axis velocity constraint (NaN means no constraint) [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'spcvy','y-axis velocity constraint (NaN means no constraint) [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'spcvz','z-axis velocity constraint (NaN means no constraint) [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'icefront','segments on ice front list (last column 0: Air, 1: Water, 2: Ice'))

		string="%s\n%s"%(string,'\n      Rift options:')
		string="%s\n%s"%(string,fielddisplay(self,'rift_penalty_threshold','threshold for instability of mechanical constraints'))
		string="%s\n%s"%(string,fielddisplay(self,'rift_penalty_lock','number of iterations before rift penalties are locked'))

		string="%s\n%s"%(string,'\n      Penalty options:')
		string="%s\n%s"%(string,fielddisplay(self,'penalty_factor','offset used by penalties: penalty = Kmax*10^offset'))
		string="%s\n%s"%(string,fielddisplay(self,'vertex_pairing','pairs of vertices that are penalized'))

		string="%s\n%s"%(string,'\n      Other:')
		string="%s\n%s"%(string,fielddisplay(self,'shelf_dampening','use dampening for floating ice ? Only for FS model'))
		string="%s\n%s"%(string,fielddisplay(self,'FSreconditioning','multiplier for incompressibility equation. Only for FS model'))
		string="%s\n%s"%(string,fielddisplay(self,'referential','local referential'))
		string="%s\n%s"%(string,fielddisplay(self,'loadingforce','loading force applied on each point [N/m^3]'))
		string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','additional outputs requested'))

		return string
		#}}}
	def extrude(self,md): # {{{
		self.spcvx=project3d(md,'vector',self.spcvx,'type','node')
		self.spcvy=project3d(md,'vector',self.spcvy,'type','node')
		self.spcvz=project3d(md,'vector',self.spcvz,'type','node')
		self.referential=project3d(md,'vector',self.referential,'type','node')
		self.loadingforce=project3d(md,'vector',self.loadingforce,'type','node')

		return self
	#}}}
	def setdefaultparameters(self): # {{{
		#maximum of non-linear iterations.
		self.maxiter=100

		#Convergence criterion: absolute, relative and residual
		self.restol=10**-4
		self.reltol=0.01
		self.abstol=10

		self.FSreconditioning=10**13
		self.shelf_dampening=0

		#Penalty factor applied kappa=max(stiffness matrix)*10^penalty_factor
		self.penalty_factor=3

		#coefficient to update the viscosity between each iteration of
		#a stressbalance according to the following formula
		#viscosity(n)=viscosity(n)+viscosity_overshoot(viscosity(n)-viscosity(n-1))
		self.viscosity_overshoot=0

		#Stop the iterations of rift if below a threshold
		self.rift_penalty_threshold=0

		#in some solutions, it might be needed to stop a run when only
		#a few constraints remain unstable. For thermal computation, this
		#parameter is often used.
		self.rift_penalty_lock=10

		#output default:
		self.requested_outputs=['default']

		return self
	#}}}
	def defaultoutputs(self,md): # {{{

		if md.mesh.dimension()==3:
			list = ['Vx','Vy','Vz','Vel','Pressure']
		else:
			list = ['Vx','Vy','Vel','Pressure']
		return list

	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if 'StressbalanceAnalysis' not in analyses:
			return md

		md = checkfield(md,'fieldname','stressbalance.spcvx','Inf',1,'timeseries',1)
		md = checkfield(md,'fieldname','stressbalance.spcvy','Inf',1,'timeseries',1)
		if m.strcmp(md.mesh.domaintype(),'3D'):
			md = checkfield(md,'fieldname','stressbalance.spcvz','Inf',1,'timeseries',1)
		md = checkfield(md,'fieldname','stressbalance.restol','size',[1],'>',0)
		md = checkfield(md,'fieldname','stressbalance.reltol','size',[1])
		md = checkfield(md,'fieldname','stressbalance.abstol','size',[1])
		md = checkfield(md,'fieldname','stressbalance.isnewton','numel',[1],'values',[0,1,2])
		md = checkfield(md,'fieldname','stressbalance.FSreconditioning','size',[1],'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','stressbalance.viscosity_overshoot','size',[1],'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','stressbalance.maxiter','size',[1],'>=',1)
		md = checkfield(md,'fieldname','stressbalance.referential','size',[md.mesh.numberofvertices,6])
		md = checkfield(md,'fieldname','stressbalance.loadingforce','size',[md.mesh.numberofvertices,3])
		md = checkfield(md,'fieldname','stressbalance.requested_outputs','stringrow',1);

		#singular solution
#		if ~any((~isnan(md.stressbalance.spcvx)+~isnan(md.stressbalance.spcvy))==2),
		if not np.any(np.logical_and(np.logical_not(np.isnan(md.stressbalance.spcvx)),np.logical_not(np.isnan(md.stressbalance.spcvy)))):
			print "\n !!! Warning: no spc applied, model might not be well posed if no basal friction is applied, check for solution crash\n"
		#CHECK THAT EACH LINES CONTAINS ONLY NAN VALUES OR NO NAN VALUES
#		if any(sum(isnan(md.stressbalance.referential),2)~=0 & sum(isnan(md.stressbalance.referential),2)~=6),
		if np.any(np.logical_and(np.sum(np.isnan(md.stressbalance.referential),axis=1)!=0,np.sum(np.isnan(md.stressbalance.referential),axis=1)!=6)):
			md.checkmessage("Each line of stressbalance.referential should contain either only NaN values or no NaN values")
		#CHECK THAT THE TWO VECTORS PROVIDED ARE ORTHOGONAL
#		if any(sum(isnan(md.stressbalance.referential),2)==0),
		if np.any(np.sum(np.isnan(md.stressbalance.referential),axis=1)==0):
			pos=[i for i,item in enumerate(np.sum(np.isnan(md.stressbalance.referential),axis=1)) if item==0]
#			np.inner (and np.dot) calculate all the dot product permutations, resulting in a full matrix multiply
#			if np.any(np.abs(np.inner(md.stressbalance.referential[pos,0:2],md.stressbalance.referential[pos,3:5]).diagonal())>sys.float_info.epsilon):
#				md.checkmessage("Vectors in stressbalance.referential (columns 1 to 3 and 4 to 6) must be orthogonal")
			for item in md.stressbalance.referential[pos,:]:
				if np.abs(np.inner(item[0:2],item[3:5]))>sys.float_info.epsilon:
					md.checkmessage("Vectors in stressbalance.referential (columns 1 to 3 and 4 to 6) must be orthogonal")
		#CHECK THAT NO rotation specified for FS Grounded ice at base
		if m.strcmp(md.mesh.domaintype(),'3D') and md.flowequation.isFS:
			pos=np.nonzero(np.logical_and(md.mask.groundedice_levelset,md.mesh.vertexonbase))
			if np.any(np.logical_not(np.isnan(md.stressbalance.referential[pos,:]))):
				md.checkmessage("no referential should be specified for basal vertices of grounded ice")

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','vertex_pairing','format','DoubleMat','mattype',3)

		yts=md.constants.yts

		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','spcvx','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','spcvy','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','spcvz','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','restol','format','Double')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','reltol','format','Double')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','abstol','format','Double','scale',1./yts)
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','isnewton','format','Integer')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','FSreconditioning','format','Double')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','viscosity_overshoot','format','Double')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','maxiter','format','Integer')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','shelf_dampening','format','Integer')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','penalty_factor','format','Double')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','rift_penalty_lock','format','Integer')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','rift_penalty_threshold','format','Integer')
		WriteData(fid,prefix,'object',self,'class','stressbalance','fieldname','referential','format','DoubleMat','mattype',1)
		
		if isinstance(self.loadingforce, (list, tuple, np.ndarray)):
			lx=self.loadingforce[:,0];
			ly=self.loadingforce[:,1];
			lz=self.loadingforce[:,2];
		else:
			lx=float('NaN'); ly=float('NaN'); lz=float('NaN');

		WriteData(fid,prefix,'data',lx,'format','DoubleMat','mattype',1,'name','md.stressbalance.loadingforcex')
		WriteData(fid,prefix,'data',ly,'format','DoubleMat','mattype',1,'name','md.stressbalance.loadingforcey')
		WriteData(fid,prefix,'data',lz,'format','DoubleMat','mattype',1,'name','md.stressbalance.loadingforcez')

		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.stressbalance.requested_outputs','format','StringArray')
	# }}}

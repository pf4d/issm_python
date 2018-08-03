import numpy as np
from issm.project3d import project3d
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData
from issm.supportedcontrols import supportedcontrols
from issm.supportedcostfunctions import supportedcostfunctions
from issm.marshallcostfunctions import marshallcostfunctions

class inversion(object):
	"""
	INVERSION class definition

	   Usage:
	      inversion=inversion()
	"""

	def __init__(self): # {{{
		self.iscontrol                   = 0
		self.incomplete_adjoint          = 0
		self.control_parameters          = float('NaN')
		self.nsteps                      = 0
		self.maxiter_per_step            = float('NaN')
		self.cost_functions              = '' 
		self.cost_functions_coefficients = float('NaN')
		self.gradient_scaling            = float('NaN')
		self.cost_function_threshold     = 0
		self.min_parameters              = float('NaN')
		self.max_parameters              = float('NaN')
		self.step_threshold              = float('NaN')
		self.vx_obs                      = float('NaN')
		self.vy_obs                      = float('NaN')
		self.vz_obs                      = float('NaN')
		self.vel_obs                     = float('NaN')
		self.thickness_obs               = float('NaN')
		self.surface_obs                 = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   inversion parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'iscontrol','is inversion activated?'))
		string="%s\n%s"%(string,fielddisplay(self,'incomplete_adjoint','1: linear viscosity, 0: non-linear viscosity'))
		string="%s\n%s"%(string,fielddisplay(self,'control_parameters','ex: {''FrictionCoefficient''}, or {''MaterialsRheologyBbar''}'))
		string="%s\n%s"%(string,fielddisplay(self,'nsteps','number of optimization searches'))
		string="%s\n%s"%(string,fielddisplay(self,'cost_functions','indicate the type of response for each optimization step'))
		string="%s\n%s"%(string,fielddisplay(self,'cost_functions_coefficients','cost_functions_coefficients applied to the misfit of each vertex and for each control_parameter'))
		string="%s\n%s"%(string,fielddisplay(self,'cost_function_threshold','misfit convergence criterion. Default is 1%, NaN if not applied'))
		string="%s\n%s"%(string,fielddisplay(self,'maxiter_per_step','maximum iterations during each optimization step'))
		string="%s\n%s"%(string,fielddisplay(self,'gradient_scaling','scaling factor on gradient direction during optimization, for each optimization step'))
		string="%s\n%s"%(string,fielddisplay(self,'step_threshold','decrease threshold for misfit, default is 30%'))
		string="%s\n%s"%(string,fielddisplay(self,'min_parameters','absolute minimum acceptable value of the inversed parameter on each vertex'))
		string="%s\n%s"%(string,fielddisplay(self,'max_parameters','absolute maximum acceptable value of the inversed parameter on each vertex'))
		string="%s\n%s"%(string,fielddisplay(self,'vx_obs','observed velocity x component [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vy_obs','observed velocity y component [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vel_obs','observed velocity magnitude [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'thickness_obs','observed thickness [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'surface_obs','observed surface elevation [m]'))
		string="%s\n%s"%(string,'Available cost functions:')
		string="%s\n%s"%(string,'   101: SurfaceAbsVelMisfit')
		string="%s\n%s"%(string,'   102: SurfaceRelVelMisfit')
		string="%s\n%s"%(string,'   103: SurfaceLogVelMisfit')
		string="%s\n%s"%(string,'   104: SurfaceLogVxVyMisfit')
		string="%s\n%s"%(string,'   105: SurfaceAverageVelMisfit')
		string="%s\n%s"%(string,'   201: ThicknessAbsMisfit')
		string="%s\n%s"%(string,'   501: DragCoefficientAbsGradient')
		string="%s\n%s"%(string,'   502: RheologyBbarAbsGradient')
		string="%s\n%s"%(string,'   503: ThicknessAbsGradient')
		return string
		#}}}
	def extrude(self,md): # {{{
		self.vx_obs=project3d(md,'vector',self.vx_obs,'type','node')
		self.vy_obs=project3d(md,'vector',self.vy_obs,'type','node')
		self.vel_obs=project3d(md,'vector',self.vel_obs,'type','node')
		self.thickness_obs=project3d(md,'vector',self.thickness_obs,'type','node')
		if not np.any(np.isnan(self.cost_functions_coefficients)):
			self.cost_functions_coefficients=project3d(md,'vector',self.cost_functions_coefficients,'type','node')
		if not np.any(np.isnan(self.min_parameters)):
			self.min_parameters=project3d(md,'vector',self.min_parameters,'type','node')
		if not np.any(np.isnan(self.max_parameters)):
			self.max_parameters=project3d(md,'vector',self.max_parameters,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{
		
		#default is incomplete adjoint for now
		self.incomplete_adjoint=1

		#parameter to be inferred by control methods (only
		#drag and B are supported yet)
		self.control_parameters='FrictionCoefficient'

		#number of steps in the control methods
		self.nsteps=20

		#maximum number of iteration in the optimization algorithm for
		#each step
		self.maxiter_per_step=20*np.ones(self.nsteps)

		#the inversed parameter is updated as follows:
		#new_par=old_par + gradient_scaling(n)*C*gradient with C in [0 1];
		#usually the gradient_scaling must be of the order of magnitude of the 
		#inversed parameter (10^8 for B, 50 for drag) and can be decreased
		#after the first iterations
		self.gradient_scaling=50*np.ones((self.nsteps,1))

		#several responses can be used:
		self.cost_functions=[101,]

		#step_threshold is used to speed up control method. When
		#misfit(1)/misfit(0) < self.step_threshold, we go directly to
		#the next step
		self.step_threshold=.7*np.ones(self.nsteps) #30 per cent decrement

		#cost_function_threshold is a criteria to stop the control methods.
		#if J[n]-J[n-1]/J[n] < criteria, the control run stops
		#NaN if not applied
		self.cost_function_threshold=float('NaN')    #not activated 

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if not self.iscontrol:
			return md

		num_controls=np.size(md.inversion.control_parameters)
		num_costfunc=np.size(md.inversion.cost_functions)

		md = checkfield(md,'fieldname','inversion.iscontrol','values',[0,1])
		md = checkfield(md,'fieldname','inversion.incomplete_adjoint','values',[0,1])
		md = checkfield(md,'fieldname','inversion.control_parameters','cell',1,'values',supportedcontrols())
		md = checkfield(md,'fieldname','inversion.nsteps','numel',[1],'>=',0)
		md = checkfield(md,'fieldname','inversion.maxiter_per_step','size',[md.inversion.nsteps],'>=',0)
		md = checkfield(md,'fieldname','inversion.step_threshold','size',[md.inversion.nsteps])
		md = checkfield(md,'fieldname','inversion.cost_functions','size',[num_costfunc],'values',supportedcostfunctions())
		md = checkfield(md,'fieldname','inversion.cost_functions_coefficients','size',[md.mesh.numberofvertices,num_costfunc],'>=',0)
		md = checkfield(md,'fieldname','inversion.gradient_scaling','size',[md.inversion.nsteps,num_controls])
		md = checkfield(md,'fieldname','inversion.min_parameters','size',[md.mesh.numberofvertices,num_controls])
		md = checkfield(md,'fieldname','inversion.max_parameters','size',[md.mesh.numberofvertices,num_controls])

		#Only SSA, HO and FS are supported right now
		if solution=='StressbalanceSolution':
			if not (md.flowequation.isSSA or md.flowequation.isHO or md.flowequation.isFS or md.flowequation.isL1L2):
				md.checkmessage("'inversion can only be performed for SSA, HO or FS ice flow models");

		if solution=='BalancethicknessSolution':
			md = checkfield(md,'fieldname','inversion.thickness_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
		else:
			md = checkfield(md,'fieldname','inversion.vx_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
			md = checkfield(md,'fieldname','inversion.vy_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'name','md.inversion.type','data',0,'format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','iscontrol','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','incomplete_adjoint','format','Boolean')
		if not self.iscontrol:
			return
		WriteData(fid,prefix,'object',self,'fieldname','nsteps','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','maxiter_per_step','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'fieldname','cost_functions_coefficients','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','gradient_scaling','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'fieldname','cost_function_threshold','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','min_parameters','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'fieldname','max_parameters','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'fieldname','step_threshold','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'fieldname','vx_obs','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','vy_obs','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','vz_obs','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','thickness_obs','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','surface_obs','format','DoubleMat','mattype',1)

		#process control parameters
		num_control_parameters=len(self.control_parameters)
		WriteData(fid,prefix,'object',self,'fieldname','control_parameters','format','StringArray')
		WriteData(fid,prefix,'data',num_control_parameters,'name','md.inversion.num_control_parameters','format','Integer')

		#process cost functions
		num_cost_functions=np.size(self.cost_functions)
		data=marshallcostfunctions(self.cost_functions)
		WriteData(fid,prefix,'data',data,'name','md.inversion.cost_functions','format','StringArray')
		WriteData(fid,prefix,'data',num_cost_functions,'name','md.inversion.num_cost_functions','format','Integer')
	# }}}

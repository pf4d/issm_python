import numpy as np
from issm.project3d              import project3d
from issm.fielddisplay           import fielddisplay
from issm.checkfield             import checkfield
from issm.WriteData              import WriteData
from issm.supportedcontrols      import supportedcontrols
from issm.supportedcostfunctions import supportedcostfunctions
from issm.marshallcostfunctions  import marshallcostfunctions

class m1qn3inversion(object):
	'''
	M1QN3 class definition

   Usage:
      m1qn3inversion=m1qn3inversion()
	'''

	def __init__(self,*args): # {{{

		if not len(args):
			print 'empty init'
			self.iscontrol                   = 0
			self.incomplete_adjoint          = 0
			self.control_parameters          = float('NaN')
			self.control_scaling_factors     = float('NaN')
			self.maxsteps                    = 0
			self.maxiter                     = 0
			self.dxmin                       = 0.
			self.gttol                       = 0.
			self.cost_functions              = float('NaN')
			self.cost_functions_coefficients = float('NaN')
			self.min_parameters              = float('NaN')
			self.max_parameters              = float('NaN')
			self.vx_obs                      = float('NaN')
			self.vy_obs                      = float('NaN')
			self.vz_obs                      = float('NaN')
			self.vel_obs                     = float('NaN')
			self.thickness_obs               = float('NaN')

			#set defaults
			self.setdefaultparameters()
		elif len(args)==1 and args[0].__module__=='issm.inversion':
			print 'converting inversion to m1qn3inversion'
			inv=args[0]
			#first call setdefaultparameters: 
			self.setdefaultparameters()

			#then go fish whatever is available in the inversion object provided to the constructor
			self.iscontrol                   = inv.iscontrol
			self.incomplete_adjoint          = inv.incomplete_adjoint
			self.control_parameters          = inv.control_parameters
			self.maxsteps                    = inv.nsteps
			self.cost_functions              = inv.cost_functions
			self.cost_functions_coefficients = inv.cost_functions_coefficients
			self.min_parameters              = inv.min_parameters
			self.max_parameters              = inv.max_parameters
			self.vx_obs                      = inv.vx_obs
			self.vy_obs                      = inv.vy_obs
			self.vz_obs                      = inv.vz_obs
			self.vel_obs                     = inv.vel_obs
			self.thickness_obs               = inv.thickness_obs
		else:
			raise Exception('constructor not supported')
		#}}}
	def __repr__(self): # {{{
		string='   m1qn3inversion parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'iscontrol','is inversion activated?'))
		string="%s\n%s"%(string,fielddisplay(self,'incomplete_adjoint','1: linear viscosity, 0: non-linear viscosity'))
		string="%s\n%s"%(string,fielddisplay(self,'control_parameters','ex: [''FrictionCoefficient''], or [''MaterialsRheologyBbar'']'))
		string="%s\n%s"%(string,fielddisplay(self,'control_scaling_factors','order of magnitude of each control (useful for multi-parameter optimization)'))
		string="%s\n%s"%(string,fielddisplay(self,'maxsteps','maximum number of iterations (gradient computation)'))
		string="%s\n%s"%(string,fielddisplay(self,'maxiter','maximum number of Function evaluation (forward run)'))
		string="%s\n%s"%(string,fielddisplay(self,'dxmin','convergence criterion: two points less than dxmin from eachother (sup-norm) are considered identical'))
		string="%s\n%s"%(string,fielddisplay(self,'gttol','||g(X)||/||g(X0)|| (g(X0): gradient at initial guess X0)'))
		string="%s\n%s"%(string,fielddisplay(self,'cost_functions','indicate the type of response for each optimization step'))
		string="%s\n%s"%(string,fielddisplay(self,'cost_functions_coefficients','cost_functions_coefficients applied to the misfit of each vertex and for each control_parameter'))
		string="%s\n%s"%(string,fielddisplay(self,'min_parameters','absolute minimum acceptable value of the inversed parameter on each vertex'))
		string="%s\n%s"%(string,fielddisplay(self,'max_parameters','absolute maximum acceptable value of the inversed parameter on each vertex'))
		string="%s\n%s"%(string,fielddisplay(self,'vx_obs','observed velocity x component [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vy_obs','observed velocity y component [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vel_obs','observed velocity magnitude [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'thickness_obs','observed thickness [m]'))
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
		
		#Scaling factor for each control
		self.control_scaling_factors=1

		#number of iterations
		self.maxsteps=20
		self.maxiter=40

		#several responses can be used:
		self.cost_functions=101

		#m1qn3 parameters
		self.dxmin  = 0.1
		self.gttol = 1e-4

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
		md = checkfield(md,'fieldname','inversion.control_scaling_factors','size',[num_controls],'>',0,'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','inversion.maxsteps','numel',[1],'>=',0)
		md = checkfield(md,'fieldname','inversion.maxiter','numel',[1],'>=',0)
		md = checkfield(md,'fieldname','inversion.dxmin','numel',[1],'>',0.)
		md = checkfield(md,'fieldname','inversion.gttol','numel',[1],'>',0.)
		md = checkfield(md,'fieldname','inversion.cost_functions','size',[num_costfunc],'values',supportedcostfunctions())
		md = checkfield(md,'fieldname','inversion.cost_functions_coefficients','size',[md.mesh.numberofvertices,num_costfunc],'>=',0)
		md = checkfield(md,'fieldname','inversion.min_parameters','size',[md.mesh.numberofvertices,num_controls])
		md = checkfield(md,'fieldname','inversion.max_parameters','size',[md.mesh.numberofvertices,num_controls])

		if solution=='BalancethicknessSolution':
			md = checkfield(md,'fieldname','inversion.thickness_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
		else:
			md = checkfield(md,'fieldname','inversion.vx_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
			md = checkfield(md,'fieldname','inversion.vy_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','iscontrol','format','Boolean')
		WriteData(fid,prefix,'name','md.inversion.type','data',2,'format','Integer')
		if not self.iscontrol:
			return
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','incomplete_adjoint','format','Boolean')
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','control_scaling_factors','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','maxsteps','format','Integer')
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','maxiter','format','Integer')
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','dxmin','format','Double')
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','gttol','format','Double')
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','cost_functions_coefficients','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','min_parameters','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','max_parameters','format','DoubleMat','mattype',3)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','vx_obs','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','vy_obs','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','vz_obs','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'class','inversion','fieldname','thickness_obs','format','DoubleMat','mattype',1)

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

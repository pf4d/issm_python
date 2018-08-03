import numpy as np
from project3d import project3d
from WriteData import WriteData
from checkfield import checkfield
from fielddisplay import fielddisplay
from IssmConfig import IssmConfig
from marshallcostfunctions import marshallcostfunctions


class taoinversion:
	def __init__(self):
		iscontrol                   = 0
		incomplete_adjoint          = 0
		control_parameters          = float('NaN')
		maxsteps                    = 0
		maxiter                     = 0
		fatol                       = 0
		frtol                       = 0
		gatol                       = 0
		grtol                       = 0
		gttol                       = 0
		algorithm                   = ''
		cost_functions              = float('NaN')
		cost_functions_coefficients = float('NaN')
		min_parameters              = float('NaN')
		max_parameters              = float('NaN')
		vx_obs                      = float('NaN')
		vy_obs                      = float('NaN')
		vz_obs                      = float('NaN')
		vel_obs                     = float('NaN')
		thickness_obs               = float('NaN')
		surface_obs                 = float('NaN')

	def __repr__(self):
		string = '   taoinversion parameters:'
		string = "%s\n\%s"%(string, fieldstring(self,'iscontrol','is inversion activated?'))
		string="%s\n%s"%(string,fieldstring(self,'mantle_viscosity','mantle viscosity constraints (NaN means no constraint) (Pa s)'))
		string="%s\n%s"%(string,fieldstring(self,'lithosphere_thickness','lithosphere thickness constraints (NaN means no constraint) (m)'))
		string="%s\n%s"%(string,fieldstring(self,'cross_section_shape',"1: square-edged, 2: elliptical-edged surface"))
		string="%s\n%s"%(string,fieldstring(self,'incomplete_adjoint','1: linear viscosity, 0: non-linear viscosity'))
		string="%s\n%s"%(string,fieldstring(self,'control_parameters','ex: {''FrictionCoefficient''}, or {''MaterialsRheologyBbar''}'))
		string="%s\n%s"%(string,fieldstring(self,'maxsteps','maximum number of iterations (gradient computation)'))
		string="%s\n%s"%(string,fieldstring(self,'maxiter','maximum number of Function evaluation (forward run)'))
		string="%s\n%s"%(string,fieldstring(self,'fatol','convergence criterion: f(X)-f(X*) (X: current iteration, X*: "true" solution, f: cost function)'))
		string="%s\n%s"%(string,fieldstring(self,'frtol','convergence criterion: |f(X)-f(X*)|/|f(X*)|'))
		string="%s\n%s"%(string,fieldstring(self,'gatol','convergence criterion: ||g(X)|| (g: gradient of the cost function)'))
		string="%s\n%s"%(string,fieldstring(self,'grtol','convergence criterion: ||g(X)||/|f(X)|'))
		string="%s\n%s"%(string,fieldstring(self,'gttol','convergence criterion: ||g(X)||/||g(X0)|| (g(X0): gradient at initial guess X0)'))
		string="%s\n%s"%(string,fieldstring(self,'algorithm','minimization algorithm: ''tao_blmvm'', ''tao_cg'', ''tao_lmvm'''))
		string="%s\n%s"%(string,fieldstring(self,'cost_functions','indicate the type of response for each optimization step'))
		string="%s\n%s"%(string,fieldstring(self,'cost_functions_coefficients','cost_functions_coefficients applied to the misfit of each vertex and for each control_parameter'))
		string="%s\n%s"%(string,fieldstring(self,'min_parameters','absolute minimum acceptable value of the inversed parameter on each vertex'))
		string="%s\n%s"%(string,fieldstring(self,'max_parameters','absolute maximum acceptable value of the inversed parameter on each vertex'))
		string="%s\n%s"%(string,fieldstring(self,'vx_obs','observed velocity x component [m/yr]'))
		string="%s\n%s"%(string,fieldstring(self,'vy_obs','observed velocity y component [m/yr]'))
		string="%s\n%s"%(string,fieldstring(self,'vel_obs','observed velocity magnitude [m/yr]'))
		string="%s\n%s"%(string,fieldstring(self,'thickness_obs','observed thickness [m]'))
		string="%s\n%s"%(string,fieldstring(self,'surface_obs','observed surface elevation [m]'))
		string="%s\n%s"%(string,'Available cost functions:')
		string="%s\n%s"%(string, '   101: SurfaceAbsVelMisfit')
		string="%s\n%s"%(string, '   102: SurfaceRelVelMisfit')
		string="%s\n%s"%(string, '   103: SurfaceLogVelMisfit')
		string="%s\n%s"%(string, '   104: SurfaceLogVxVyMisfit')
		string="%s\n%s"%(string, '   105: SurfaceAverageVelMisfit')
		string="%s\n%s"%(string, '   201: ThicknessAbsMisfit')
		string="%s\n%s"%(string, '   501: DragCoefficientAbsGradient')
		string="%s\n%s"%(string, '   502: RheologyBbarAbsGradient')
		string="%s\n%s"%(string, '   503: ThicknessAbsGradient')
		return string
	def setdefaultparameters(self):

		#default is incomplete adjoint for now
		self.incomplete_adjoint=1

		#parameter to be inferred by control methods (only
		#drag and B are supported yet)
		self.control_parameters=['FrictionCoefficient']

		#number of iterations and steps
		self.maxsteps=20;
		self.maxiter =30;

		#default tolerances
		self.fatol = 0;
		self.frtol = 0;
		self.gatol = 0;
		self.grtol = 0;
		self.gttol = 1e-4;

		#minimization algorithm
		PETSCMAJOR = IssmConfig('_PETSC_MAJOR_')[0]
		PETSCMINOR = IssmConfig('_PETSC_MINOR_')[0]
		if(PETSCMAJOR>3 or (PETSCMAJOR==3 and PETSCMINOR>=5)):
			self.algorithm = 'blmvm';
		else:
			self.algorithm = 'tao_blmvm';
		
		#several responses can be used:
		self.cost_functions=101;

		return self

	def extrude(self,md):
		self.vx_obs=project3d(md,'vector',self.vx_obs,'type','node')
		self.vy_obs=project3d(md,'vector',self.vy_obs,'type','node')
		self.vel_obs=project3d(md,'vector',self.vel_obs,'type','node')
		self.thickness_obs=project3d(md,'vector',self.thickness_obs,'type','node')

		if numel(self.cost_functions_coefficients) > 1:
			self.cost_functions_coefficients=project3d(md,'vector',self.cost_functions_coefficients,'type','node')
		
		if numel(self.min_parameters) > 1:
			self.min_parameters=project3d(md,'vector',self.min_parameters,'type','node')
		
		if numel(self.max_parameters)>1:
			self.max_parameters=project3d(md,'vector',self.max_parameters,'type','node')

		return self

	def checkconsistency(self,md,solution,analyses):
		if not self.control:
			return md
		if not IssmConfig('_HAVE_TAO_')[0]:
			md = checkmessage(md,['TAO has not been installed, ISSM needs to be reconfigured and recompiled with TAO'])


		num_controls= np.numel(md.inversion.control_parameters)
		num_costfunc= np.size(md.inversion.cost_functions,2)

		md = checkfield(md,'fieldname','inversion.iscontrol','values',[0, 1])
		md = checkfield(md,'fieldname','inversion.incomplete_adjoint','values',[0, 1])
		md = checkfield(md,'fieldname','inversion.control_parameters','cell',1,'values',supportedcontrols())
		md = checkfield(md,'fieldname','inversion.maxsteps','numel',1,'>=',0)
		md = checkfield(md,'fieldname','inversion.maxiter','numel',1,'>=',0)
		md = checkfield(md,'fieldname','inversion.fatol','numel',1,'>=',0)
		md = checkfield(md,'fieldname','inversion.frtol','numel',1,'>=',0)
		md = checkfield(md,'fieldname','inversion.gatol','numel',1,'>=',0)
		md = checkfield(md,'fieldname','inversion.grtol','numel',1,'>=',0)
		md = checkfield(md,'fieldname','inversion.gttol','numel',1,'>=',0)


		PETSCMAJOR = IssmConfig('_PETSC_MAJOR_')[0]
		PETSCMINOR = IssmConfig('_PETSC_MINOR_')[0]
		if(PETSCMAJOR>3 or (PETSCMAJOR==3 and PETSCMINOR>=5)):
			md = checkfield(md,'fieldname','inversion.algorithm','values',{'blmvm','cg','lmvm'})
		else:
			md = checkfield(md,'fieldname','inversion.algorithm','values',{'tao_blmvm','tao_cg','tao_lmvm'})


		md = checkfield(md,'fieldname','inversion.cost_functions','size',[1, num_costfunc],'values',supportedcostfunctions())
		md = checkfield(md,'fieldname','inversion.cost_functions_coefficients','size',[md.mesh.numberofvertices, num_costfunc],'>=',0)
		md = checkfield(md,'fieldname','inversion.min_parameters','size',[md.mesh.numberofvertices, num_controls])
		md = checkfield(md,'fieldname','inversion.max_parameters','size',[md.mesh.numberofvertices, num_controls])


		if solution=='BalancethicknessSolution':
			md = checkfield(md,'fieldname','inversion.thickness_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
		elif solution=='BalancethicknessSoftSolution':
			md = checkfield(md,'fieldname','inversion.thickness_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
		else:
			md = checkfield(md,'fieldname','inversion.vx_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
			md = checkfield(md,'fieldname','inversion.vy_obs','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		def marshall(self, md, fid):

			yts=md.constants.yts;
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','iscontrol','format','Boolean')
			WriteData(fid,prefix,'name','md.inversion.type','data',1,'format','Integer')
			if not self.iscontrol:
				return
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','incomplete_adjoint','format','Boolean')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','maxsteps','format','Integer')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','maxiter','format','Integer')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','fatol','format','Double')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','frtol','format','Double')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','gatol','format','Double')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','grtol','format','Double')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','gttol','format','Double')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','algorithm','format','String')
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','cost_functions_coefficients','format','DoubleMat','mattype',1)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','min_parameters','format','DoubleMat','mattype',3)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','max_parameters','format','DoubleMat','mattype',3)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','vx_obs','format','DoubleMat','mattype',1,'scale',1./yts)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','vy_obs','format','DoubleMat','mattype',1,'scale',1./yts)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','vz_obs','format','DoubleMat','mattype',1,'scale',1./yts)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','thickness_obs','format','DoubleMat','mattype',1)
			WriteData(fid,prefix,'object',self,'class','inversion','fieldname','surface_obs','format','DoubleMat','mattype',1)

			#process control parameters
			num_control_parameters = np.numel(self.control_parameters)
			WriteData(fid,prefix,'object',self,'fieldname','control_parameters','format','StringArray')
			WriteData(fid,prefix,'data',num_control_parameters,'name','md.inversion.num_control_parameters','format','Integer')

			#process cost functions
			num_cost_functions = np.size(self.cost_functions,2)
			data= marshallcostfunctions(self.cost_functions)
			WriteData(fid,prefix,'data',data,'name','md.inversion.cost_functions','format','StringArray')
			WriteData(fid,prefix,'data',num_cost_functions,'name','md.inversion.num_cost_functions','format','Integer')

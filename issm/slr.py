from fielddisplay import fielddisplay
from MatlabFuncs import *
from model import *
import numpy as np
from checkfield import checkfield
from WriteData import WriteData

class slr(object):
	"""
	SLR class definition
	
		Usage:
		  slr=slr();
	"""
	
	def __init__(self): # {{{
		self.deltathickness    = float('NaN')
		self.sealevel          = float('NaN')
		self.maxiter           = 0
		self.reltol            = 0
		self.abstol            = 0
		self.love_h            = 0 #provided by PREM model()
		self.love_k            = 0 #ideam
		self.love_l            = 0 #ideam
		self.tide_love_h       = 0
		self.tide_love_k       = 0
		self.fluid_love        = 0; 
		self.equatorial_moi    = 0; 
		self.polar_moi	       = 0; 
		self.angular_velocity  = 0;
		self.rigid             = 0
		self.elastic           = 0
		self.rotation          = 0
		self.ocean_area_scaling = 0;
		self.degacc            = 0
		self.requested_outputs = []
		self.transitions       = []
		
		#set defaults
		self.setdefaultparameters()
		#}}}
	def __repr__(self): # {{{
			string='   slr parameters:'
			string="%s\n%s"%(string,fielddisplay(self,'deltathickness','thickness change (main loading of the slr solution core [m]'))
			string="%s\n%s"%(string,fielddisplay(self,'reltol','sea level rise relative convergence criterion, (default, NaN: not applied)'))
			string="%s\n%s"%(string,fielddisplay(self,'abstol','sea level rise absolute convergence criterion, NaN: not applied'))
			string="%s\n%s"%(string,fielddisplay(self,'maxiter','maximum number of nonlinear iterations'))
			string="%s\n%s"%(string,fielddisplay(self,'love_h','load Love number for radial displacement'))
			string="%s\n%s"%(string,fielddisplay(self,'love_k','load Love number for gravitational potential perturbation'))
			string="%s\n%s"%(string,fielddisplay(self,'love_l','load Love number for horizontal displaements'))
			string="%s\n%s"%(string,fielddisplay(self,'tide_love_k','tidal load Love number (degree 2)'))
			string="%s\n%s"%(string,fielddisplay(self,'tide_love_h','tidal load Love number (degree 2)'))
			string="%s\n%s"%(string,fielddisplay(self,'fluid_love','secular fluid Love number'))
			string="%s\n%s"%(string,fielddisplay(self,'equatorial_moi','mean equatorial moment of inertia [kg m^2]'))
			string="%s\n%s"%(string,fielddisplay(self,'polar_moi','polar moment of inertia [kg m^2]'))
			string="%s\n%s"%(string,fielddisplay(self,'angular_velocity','mean rotational velocity of earth [per second]')); 
			string="%s\n%s"%(string,fielddisplay(self,'rigid','rigid earth graviational potential perturbation'))
			string="%s\n%s"%(string,fielddisplay(self,'elastic','elastic earth graviational potential perturbation'))
			string="%s\n%s"%(string,fielddisplay(self,'rotation','earth rotational potential perturbation'))
			string="%s\n%s"%(string,fielddisplay(self,'ocean_area_scaling','correction for model representation of ocean area [default: No correction]'))
			string="%s\n%s"%(string,fielddisplay(self,'degacc','accuracy (default .01 deg) for numerical discretization of the Green''s functions'))
			string="%s\n%s"%(string,fielddisplay(self,'transitions','indices into parts of the mesh that will be icecaps'))
			string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','additional outputs requested'))

			return string
		# }}}
	def setdefaultparameters(self): # {{{
		
		#Convergence criterion: absolute, relative and residual
		self.reltol=float('NaN') #default
		self.abstol=0.001 #1 mm of sea level rise

		#maximum of non-linear iterations.
		self.maxiter=10

		#computational flags: 
		self.rigid=1
		self.elastic=1
		self.rotation=0
		self.ocean_area_scaling=0

		#tidal love numbers: 
		self.tide_love_h=0.6149; #degree 2
		self.tide_love_k=0.3055; #degree 2
		
                #secular fluid love number: 
		self.fluid_love=0.942; 
		
		#moment of inertia: 
		self.equatorial_moi=8.0077*10**37; # [kg m^2] 
		self.polar_moi	   =8.0345*10**37; # [kg m^2] 

		#mean rotational velocity of earth 
		self.angular_velocity=7.2921*10**-5; # [s^-1] 

		#numerical discretization accuracy
		self.degacc=.01
		
		#output default:
		self.requested_outputs=['default']

		#transitions should be a cell array of vectors: 
		self.transitions=[]

		#default output
		self.requested_outputs=['default']
		return self
		#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if (solution!='SealevelriseAnalysis'):
			return md

		md = checkfield(md,'fieldname','slr.deltathickness','NaN',1,'Inf',1,'size',[md.mesh.numberofelements])
		md = checkfield(md,'fieldname','slr.sealevel','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','slr.love_h','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.love_k','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.love_l','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.tide_love_h','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.tide_love_k','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.fluid_love','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.equatorial_moi','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.polar_moi','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.angular_velocity','NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','slr.reltol','size',[1,1])
		md = checkfield(md,'fieldname','slr.abstol','size',[1,1])
		md = checkfield(md,'fieldname','slr.maxiter','size',[1,1],'>=',1)
		md = checkfield(md,'fieldname','slr.degacc','size',[1,1],'>=',1e-10)
		md = checkfield(md,'fieldname','slr.requested_outputs','stringrow',1)

		#check that love numbers are provided at the same level of accuracy: 
		if (size(self.love_h,0) != size(self.love_k,0) | size(self.love_h,0) != size(self.love_l,0)):
			error('slr error message: love numbers should be provided at the same level of accuracy')
		return md
	# }}}
	def defaultoutputs(self,md): # {{{
		return ['Sealevel']
	# }}}
	def marshall(self,prefix,md,fid): # {{{
		WriteData(fid,prefix,'object',self,'fieldname','deltathickness','format','DoubleMat','mattype',2)
		WriteData(fid,prefix,'object',self,'fieldname','sealevel','mattype',1,'format','DoubleMat','timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'fieldname','reltol','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','abstol','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','maxiter','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','love_h','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','love_k','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','love_l','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','tide_love_h','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','tide_love_k','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','fluid_love','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','equatorial_moi','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','polar_moi','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','angular_velocity','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','rigid','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','elastic','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','rotation','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','ocean_area_scaling','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','degacc','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','transitions','format','MatArray')
	
		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.slr.requested_outputs','format','StringArray')
	# }}}

import numpy as np
from issm.dependent import dependent
from issm.independent import independent
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData
from issm.MatlabFuncs import *

class autodiff(object):
	"""
	AUTODIFF class definition

	   Usage:
	      autodiff=autodiff();
	"""
	def __init__(self,*args):    # {{{
		self.isautodiff   = False
		self.dependents   = []
		self.independents = []
		self.driver       = 'fos_forward'
		self.obufsize     = float('NaN')
		self.lbufsize     = float('NaN')
		self.cbufsize     = float('NaN')
		self.tbufsize     = float('NaN')
		self.gcTriggerMaxSize     = float('NaN')
		self.gcTriggerRatio     = float('NaN')
		if not len(args):
			self.setdefaultparameters()
		else:
			raise RuntimeError("constructor not supported")
	# }}}
	def __repr__(self):    # {{{
		s ="      automatic differentiation parameters:\n"

		s+="%s\n" % fielddisplay(self,'isautodiff',"indicates if the automatic differentiation is activated")
		s+="%s\n" % fielddisplay(self,'dependents',"list of dependent variables")
		s+="%s\n" % fielddisplay(self,'independents',"list of independent variables")
		s+="%s\n" % fielddisplay(self,'driver',"ADOLC driver ('fos_forward' or 'fov_forward')")
		s+="%s\n" % fielddisplay(self,'obufsize',"Number of operations per buffer (==OBUFSIZE in usrparms.h)")
		s+="%s\n" % fielddisplay(self,'lbufsize',"Number of locations per buffer (==LBUFSIZE in usrparms.h)")
		s+="%s\n" % fielddisplay(self,'cbufsize',"Number of values per buffer (==CBUFSIZE in usrparms.h)")
		s+="%s\n" % fielddisplay(self,'tbufsize',"Number of taylors per buffer (<=TBUFSIZE in usrparms.h)")
		s+="%s\n" % fielddisplay(self,'gcTriggerRatio',"free location block sorting/consolidation triggered if the ratio between allocated and used locations exceeds gcTriggerRatio")
		s+="%s\n" % fielddisplay(self,'gcTriggerMaxSize',"free location block sorting/consolidation triggered if the allocated locations exceed gcTriggerMaxSize)")

		return s
	# }}}
	def setdefaultparameters(self):    # {{{
		
		self.obufsize     = 524288
		self.lbufsize     = 524288
		self.cbufsize     = 524288
		self.tbufsize     = 524288
		self.gcTriggerRatio=2.0
		self.gcTriggerMaxSize=65536
		return self
	# }}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return 
		if not self.isautodiff:
			return md 
		
		md = checkfield(md,'fieldname','autodiff.obufsize','>=',524288)
		md = checkfield(md,'fieldname','autodiff.lbufsize','>=',524288)
		md = checkfield(md,'fieldname','autodiff.cbufsize','>=',524288)
		md = checkfield(md,'fieldname','autodiff.tbufsize','>=',524288)
		md = checkfield(md,'fieldname','autodiff.gcTriggerRatio','>=',2.0)
		md = checkfield(md,'fieldname','autodiff.gcTriggerMaxSize','>=',65536)

		#Driver value:
		md = checkfield(md,'fieldname','autodiff.driver','values',['fos_forward','fov_forward','fov_forward_all','fos_reverse','fov_reverse','fov_reverse_all'])

		#go through our dependents and independents and check consistency: 
		for dep in self.dependents:
			dep.checkconsistency(md,solution,analyses)
		for i,indep in enumerate(self.independents):
			indep.checkconsistency(md,i,solution,analyses,self.driver)

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','isautodiff','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','driver','format','String')

		#early return
		if not self.isautodiff:
			WriteData(fid,prefix,'data',False,'name','md.autodiff.mass_flux_segments_present','format','Boolean')
			WriteData(fid,prefix,'data',False,'name','md.autodiff.keep','format','Boolean')
			return
			
		#buffer sizes {{{
		WriteData(fid,prefix,'object',self,'fieldname','obufsize','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','lbufsize','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','cbufsize','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','tbufsize','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','gcTriggerRatio','format','Double');
		WriteData(fid,prefix,'object',self,'fieldname','gcTriggerMaxSize','format','Double');
		#}}}
		#process dependent variables {{{
		num_dependent_objects=len(self.dependents)
		WriteData(fid,prefix,'data',num_dependent_objects,'name','md.autodiff.num_dependent_objects','format','Integer')

		if num_dependent_objects:
			names=[]
			types=np.zeros(num_dependent_objects)
			indices=np.zeros(num_dependent_objects)

			for i,dep in enumerate(self.dependents):
				names.append(dep.name)
				types[i]=dep.typetoscalar()
				indices[i]=dep.index

			WriteData(fid,prefix,'data',names,'name','md.autodiff.dependent_object_names','format','StringArray')
			WriteData(fid,prefix,'data',types,'name','md.autodiff.dependent_object_types','format','IntMat','mattype',3)
			WriteData(fid,prefix,'data',indices,'name','md.autodiff.dependent_object_indices','format','IntMat','mattype',3)
		#}}}
		#process independent variables {{{
		num_independent_objects=len(self.independents)
		WriteData(fid,prefix,'data',num_independent_objects,'name','md.autodiff.num_independent_objects','format','Integer')

		if num_independent_objects:
			names=[None] * num_independent_objects
			types=np.zeros(num_independent_objects)

			for i,indep in enumerate(self.independents):
				names[i]=indep.name
				types[i]=indep.typetoscalar()

			WriteData(fid,prefix,'data',names,'name','md.autodiff.independent_object_names','format','StringArray')
			WriteData(fid,prefix,'data',types,'name','md.autodiff.independent_object_types','format','IntMat','mattype',3)
		#}}}
		#if driver is fos_forward, build index:  {{{
		if strcmpi(self.driver,'fos_forward'):
			index=0

			for indep in self.independents:
				if not np.isnan(indep.fos_forward_index):
					index+=indep.fos_forward_index
					break
				else:
					if strcmpi(indep.type,'scalar'):
						index+=1
					else:
						index+=indep.nods

			index-=1    #get c-index numbering going
			WriteData(fid,prefix,'data',index,'name','md.autodiff.fos_forward_index','format','Integer')
		#}}}
		#if driver is fos_reverse, build index:  {{{
		if strcmpi(self.driver,'fos_reverse'):
			index=0

			for dep in self.dependents:
				if not np.isnan(dep.fos_reverse_index):
					index+=dep.fos_reverse_index
					break
				else:
					if strcmpi(dep.type,'scalar'):
						index+=1
					else:
						index+=dep.nods

			index-=1    #get c-index numbering going
			WriteData(fid,prefix,'data',index,'name','md.autodiff.fos_reverse_index','format','Integer')
		#}}}
		#if driver is fov_forward, build indices:  {{{
		if strcmpi(self.driver,'fov_forward'):
			indices=0

			for indep in self.independents:
				if indep.fos_forward_index:
					indices+=indep.fov_forward_indices
					break
				else:
					if strcmpi(indep.type,'scalar'):
						indices+=1
					else:
						indices+=indep.nods

			indices-=1    #get c-indices numbering going
			WriteData(fid,prefix,'data',indices,'name','md.autodiff.fov_forward_indices','format','IntMat','mattype',3)
		#}}}
		#deal with mass fluxes:  {{{
		mass_flux_segments=[dep.segments for dep in self.dependents if strcmpi(dep.name,'MassFlux')]

		if mass_flux_segments:
			WriteData(fid,prefix,'data',mass_flux_segments,'name','md.autodiff.mass_flux_segments','format','MatArray')
			flag=True
		else:
			flag=False
		WriteData(fid,prefix,'data',flag,'name','md.autodiff.mass_flux_segments_present','format','Boolean')
		#}}}
		#deal with trace keep on: {{{
		keep=False

		#From ADOLC userdoc: 
		# The optional integer argument keep of trace on determines whether the numerical values of all active variables are 
		# recorded in a buffered temporary array or file called the taylor stack. This option takes effect if keep = 1 and 
		# prepares the scene for an immediately following gradient evaluation by a call to a routine implementing the reverse 
		# mode as described in the Section 4 and Section 5. 
		#

		if len(self.driver)<=3:
			keep=False    #there is no "_reverse" string within the driver string: 
		else:
			if strncmpi(self.driver[3:],'_reverse',8):
				keep=True
			else:
				keep=False
		WriteData(fid,prefix,'data',keep,'name','md.autodiff.keep','format','Boolean')
		#}}}

		return
	# }}}

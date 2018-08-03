from IssmConfig import IssmConfig
from mumpsoptions import mumpsoptions
from iluasmoptions import iluasmoptions
from fielddisplay import fielddisplay
from checkfield import checkfield
from issmgslsolver import issmgslsolver
from issmmumpssolver import issmmumpssolver

class toolkits(object):
	"""
	TOOLKITS class definition

	   Usage:
	      self=toolkits();
	"""

	def __init__(self):    # {{{
		#default toolkits
		if IssmConfig('_HAVE_PETSC_')[0]:
			#MUMPS is the default toolkits
			if IssmConfig('_HAVE_MUMPS_')[0]:
				self.DefaultAnalysis           = mumpsoptions()
			else:
				self.DefaultAnalysis           = iluasmoptions()
		else:
			if IssmConfig('_HAVE_MUMPS_')[0]:
				self.DefaultAnalysis           = issmmumpssolver()
			elif IssmConfig('_HAVE_GSL_')[0]:
				self.DefaultAnalysis           = issmgslsolver()
			else:
				raise IOError("ToolkitsFile error: need at least Mumps or Gsl to define issm solver type")

		#The other properties are dynamic
	# }}}
	def __repr__(self):    # {{{
		s ="List of toolkits options per analysis:\n\n"
		for analysis in vars(self).iterkeys():
			s+="%s\n" % fielddisplay(self,analysis,'')

		return s
	# }}}
	def addoptions(self,analysis,*args):    # {{{
		# Usage example:
		#    md.toolkits=addoptions(md.toolkits,'StressbalanceAnalysis',FSoptions());
		#    md.toolkits=addoptions(md.toolkits,'StressbalanceAnalysis');

		#Create dynamic property if property does not exist yet
		if not hasattr(self,analysis):
			setattr(self,analysis,None)

		#Add toolkits options to analysis
		if len(args)==1:
			setattr(self,analysis,args[0])

		return self
	# }}}
	def checkconsistency(self,md,solution,analyses):    # {{{
		for analysis in vars(self).iterkeys():
			if not getattr(self,analysis):
				md.checkmessage("md.toolkits.%s is empty" % analysis)

		return md
	# }}}
	def ToolkitsFile(self,filename):    # {{{
		"""
		TOOLKITSFILE- build toolkits file

		   Build a Petsc compatible options file, from the toolkits model field  + return options string
		   This file will also be used when the toolkit used is 'issm' instead of 'petsc'


		   Usage:     ToolkitsFile(toolkits,filename);
		"""

		#open file for writing
		try:
			fid=open(filename,'w')
		except IOError as e:
			raise IOError("ToolkitsFile error: could not open '%s' for writing." % filename)

		#write header
		fid.write("%s%s%s\n" % ('%Petsc options file: ',filename,' written from Matlab toolkits array'))

		#start writing options
		for analysis in vars(self).iterkeys():
			options=getattr(self,analysis)

			#first write analysis:
			fid.write("\n+%s\n" % analysis)    #append a + to recognize it's an analysis enum

			#now, write options
			for optionname,optionvalue in options.iteritems():

				if not optionvalue:
					#this option has only one argument
					fid.write("-%s\n" % optionname)
				else:
					#option with value. value can be string or scalar
					if   isinstance(optionvalue,(bool,int,long,float)):
						fid.write("-%s %g\n" % (optionname,optionvalue))
					elif isinstance(optionvalue,(str,unicode)):
						fid.write("-%s %s\n" % (optionname,optionvalue))
					else:
						raise TypeError("ToolkitsFile error: option '%s' is not well formatted." % optionname)

		fid.close()
	# }}}

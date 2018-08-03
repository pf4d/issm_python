import numpy as np
from pairoptions import pairoptions
from fielddisplay import fielddisplay
import MatlabFuncs as m

class results(object):
	"""
	RESULTS class definition

	   Usage:
	      results=results();
	"""

	def __init__(self,*args):    # {{{
		pass
	# }}}
	def __repr__(self):    # {{{
		s ="   Model results:\n"

		if 'step' in self.__dict__:
			s+="%s\n" % fielddisplay(self,'step',"step number")
		if 'time' in self.__dict__:
			s+="%s\n" % fielddisplay(self,'time',"time value")
		if 'SolutionType' in self.__dict__:
			s+="%s\n" % fielddisplay(self,'SolutionType',"solution type")

		for name in self.__dict__.iterkeys():
			if name not in ['step','time','SolutionType','errlog','outlog']:
				if   isinstance(getattr(self,name),list):
					s+="%s\n" % fielddisplay(self,name,"model results list")
				elif isinstance(getattr(self,name),results):
					s+="%s\n" % fielddisplay(self,name,"model results case")
				else:
					s+="%s\n" % fielddisplay(self,name,"")

		if 'errlog' in self.__dict__:
			s+="%s\n" % fielddisplay(self,'errlog',"error log file")
		if 'outlog' in self.__dict__:
			s+="%s\n" % fielddisplay(self,'outlog',"output log file")

		return s
	# }}}
	def setdefaultparameters(self):    # {{{
		#do nothing
		return self
	# }}}
	def checkconsistency(self,md,solution,analyses):    # {{{
		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		pass
	# }}}

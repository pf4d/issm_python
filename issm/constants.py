from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class constants(object):
	"""
	CONSTANTS class definition

	   Usage:
	      constants=constants();
	"""

	def __init__(self): # {{{
		self.g                    = 0
		self.yts                  = 0
		self.referencetemperature = 0
		
		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string="   constants parameters:"

		string="%s\n%s"%(string,fielddisplay(self,"g","gravitational acceleration [m/s^2]"))
		string="%s\n%s"%(string,fielddisplay(self,"yts","number of seconds in a year [s/yr]"))
		string="%s\n%s"%(string,fielddisplay(self,"referencetemperature","reference temperature used in the enthalpy model [K]"))

		return string
		#}}}
	def setdefaultparameters(self): # {{{
		
		#acceleration due to gravity (m/s^2)
		self.g=9.81

		#converstion from year to seconds
		self.yts=365.*24.*3600.

		#the reference temperature for enthalpy model (cf Aschwanden)
		self.referencetemperature=223.15

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		md = checkfield(md,'fieldname','constants.g','>',0,'size',[1])
		md = checkfield(md,'fieldname','constants.yts','>',0,'size',[1])
		md = checkfield(md,'fieldname','constants.referencetemperature','size',[1])

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','g','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','yts','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','referencetemperature','format','Double')
	# }}}

import os
from issm.results import results
from issm.parseresultsfromdisk import parseresultsfromdisk
import issm.MatlabFuncs as m

def loadresultsfromdisk(md,filename):
	"""
	LOADRESULTSFROMDISK - load results of solution sequence from disk file "filename"            
 
	   Usage:
	      md=loadresultsfromdisk(md=False,filename=False);
	"""

	#check number of inputs/outputs
	if not md or not filename:
		raise ValueError("loadresultsfromdisk: error message.")

	if not md.qmu.isdakota:

		#Check that file exists
		if not os.path.exists(filename):
			raise OSError("binary file '%s' not found." % filename)

		#initialize md.results if not a structure yet
		if not isinstance(md.results,results):
			md.results=results()

		#load results onto model
		structure=parseresultsfromdisk(md,filename,not md.settings.io_gather)
		if not len(structure):
			raise RuntimeError("No result found in binary file '%s'. Check for solution crash." % filename)
		setattr(md.results,structure[0].SolutionType,structure)

		#recover solution_type from results
		md.private.solution=structure[0].SolutionType

		#read log files onto fields
		if os.path.exists(md.miscellaneous.name+'.errlog'):
			with open(md.miscellaneous.name+'.errlog','r') as f:
				setattr(getattr(md.results,structure[0].SolutionType)[0],'errlog',[line[:-1] for line in f])
		else:
			setattr(getattr(md.results,structure[0].SolutionType)[0],'errlog',[])

		if os.path.exists(md.miscellaneous.name+'.outlog'):
			with open(md.miscellaneous.name+'.outlog','r') as f:
				setattr(getattr(md.results,structure[0].SolutionType)[0],'outlog',[line[:-1] for line in f])
		else:
			setattr(getattr(md.results,structure[0].SolutionType)[0],'outlog',[])

		if len(getattr(md.results,structure[0].SolutionType)[0].errlog):
			print ("loadresultsfromcluster info message: error during solution. Check your errlog and outlog model fields.")

		#if only one solution, extract it from list for user friendliness
		if len(structure) == 1 and not m.strcmp(structure[0].SolutionType,'TransientSolution'):
			setattr(md.results,structure[0].SolutionType,structure[0])

	#post processes qmu results if necessary
	else:
		md=postqmu(md)
		os.chdir('..')

	return md

def AnalysisConfiguration(solutiontype): #{{{
	"""
	ANALYSISCONFIGURATION - return type of analyses, number of analyses 

		Usage:
			[analyses]=AnalysisConfiguration(solutiontype);
	"""

	if   solutiontype == 'StressbalanceSolution':
		analyses=['StressbalanceAnalysis','StressbalanceVerticalAnalysis','StressbalanceSIAAnalysis','L2ProjectionBaseAnalysis']

	elif solutiontype == 'SteadystateSolution':
		analyses=['StressbalanceAnalysis','StressbalanceVerticalAnalysis','StressbalanceSIAAnalysis','L2ProjectionBaseAnalysis','ThermalAnalysis','MeltingAnalysis','EnthalpyAnalysis']

	elif solutiontype == 'ThermalSolution':
		analyses=['EnthalpyAnalysis','ThermalAnalysis','MeltingAnalysis']

	elif solutiontype == 'MasstransportSolution':
		analyses=['MasstransportAnalysis']

	elif solutiontype == 'BalancethicknessSolution':
		analyses=['BalancethicknessAnalysis']

	elif solutiontype == 'SurfaceSlopeSolution':
		analyses=['L2ProjectionBaseAnalysis']

	elif solutiontype == 'BalancevelocitySolution':
		analyses=['BalancevelocityAnalysis']

	elif solutiontype == 'BedSlopeSolution':
		analyses=['L2ProjectionBaseAnalysis']

	elif solutiontype == 'GiaSolution':
		analyses=['GiaIvinsAnalysis']

	elif solutiontype == 'TransientSolution':
		analyses=['StressbalanceAnalysis','StressbalanceVerticalAnalysis','StressbalanceSIAAnalysis','L2ProjectionBaseAnalysis','ThermalAnalysis','MeltingAnalysis','EnthalpyAnalysis','MasstransportAnalysis']

	elif solutiontype == 'HydrologySolution':
		analyses=['L2ProjectionBaseAnalysis','HydrologyShreveAnalysis','HydrologyDCInefficientAnalysis','HydrologyDCEfficientAnalysis']

	elif 'DamageEvolutionSolution':
		analyses=['DamageEvolutionAnalysis']

	else:
		raise TypeError("solution type: '%s' not supported yet!" % solutiontype)

	return analyses
#}}}

def ismodelselfconsistent(md):
	"""
	ISMODELSELFCONSISTENT - check that model forms a closed form solvable problem.

	   Usage:
	      ismodelselfconsistent(md),
	"""

	#initialize consistency as true
	md.private.isconsistent=True

	#Get solution and associated analyses
	solution=md.private.solution
	analyses=AnalysisConfiguration(solution)

	#Go through a model fields, check that it is a class, and call checkconsistency
	fields=vars(md)
#	for field in fields.iterkeys():
	for field in md.properties():

		#Some properties do not need to be checked
		if field in ['results','debug','radaroverlay']:
			continue

		#Check that current field is an object
		if not hasattr(getattr(md,field),'checkconsistency'):
			md.checkmessage("field '%s' is not an object." % field)

		#Check consistency of the object
		exec("md.{}.checkconsistency(md,solution,analyses)".format(field))

	#error message if mode is not consistent
	if not md.private.isconsistent:
		raise RuntimeError('Model not consistent, see messages above.')


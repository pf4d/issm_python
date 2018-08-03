from ElementConnectivity_python import ElementConnectivity_python

def ElementConnectivity(elements,nodeconnectivity):
	"""
	ELEMENTCONNECTIVITY - Build element connectivity using node connectivity and elements

		Usage:
			elementconnectivity = ElementConnectivity(elements,nodeconnectivity);
	"""
	#Call mex module
	elementconnectivity = ElementConnectivity_python(elements,nodeconnectivity)
	
	#Return
	return elementconnectivity

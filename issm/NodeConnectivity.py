from NodeConnectivity_python import NodeConnectivity_python

def NodeConnectivity(elements,numnodes):
	"""
	NODECONNECTIVITY - Build node connectivity from elements

		Usage:
			connectivity = NodeConnectivity(elements, numnodes);
	"""
	# Call mex module
	connectivity = NodeConnectivity_python(elements,numnodes)

	# Return
	return connectivity


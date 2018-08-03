Hello ISSM
===========

We begin with an example that does not require any external data; the "`Ice Sheet Model Intercomparison Project for Higher-Order Models <http://homepages.ulb.ac.be/~fpattyn/ismip/>`_".

Set up the model
----------------

First, import all the packages we will need::

  from squaremesh      import squaremesh
  from model           import model
  from solve           import solve
  from setmask         import setmask
  from setflowequation import setflowequation
  from verbose         import verbose
  from SetIceSheetBC   import SetIceSheetBC
  from socket          import gethostname
  from generic         import generic
  from fenics_viz      import *
  import numpy             as np
  import matplotlib.pyplot as plt
  import matplotlib.tri    as tri
  import os

First, create an empty :class:`~model.model` instance and name the simulation::

  md = model()
  md.miscellaneous.name = 'ISMIP_HOM_A'
  
Next, we make a simple three-dimensional box mesh with 49 cells in the :math:`x` and :math:`y` directions over a width of 8 km using :class:`~squaremesh.squaremesh`::

  L  = 80000.0
  n  = 50
  md = squaremesh(md, L, L, n, n)

Let the entire domain be defined over grounded ice with :class:`~setmask.setmask`::

  md = setmask(md, 'all', '')

The ISMIP-HOM experiment "A" geometry is created by directly editing the coordinates of the :class:`~mesh2d.mesh2d` instance created above::
  
  # surface :
  md.geometry.surface = - md.mesh.x * np.tan(0.5*np.pi/180.0)
  
  # base of ice sheet with 'L' the size of the side of the square :
  md.geometry.base = + md.geometry.surface - 1000.0 \
                     + 500.0 * np.sin(md.mesh.x*2*np.pi/L) \
                             * np.sin(md.mesh.y*2*np.pi/L)
  
  # thickness is the difference between surface and base :
  md.geometry.thickness = md.geometry.surface - md.geometry.base

The material parameters may be changed to match those of the ISMIP HOM experiment by changing either the :class:`~model.model`'s :class:`~constants.constants` or material properties :class:`~matice.matice`::

  md.materials.rho_ice    = 910.0              # ice density
  md.constants.g          = 9.80665            # gravitational acc.
  md.constants.yts        = 31556926.0         # seconds per year
  n                       = 3.0                # Glen's flow exponent
  spy                     = md.constants.yts   # s a^{-1}
  A                       = 1e-16              # Pa^{-n} s^{-1}
  B                       = (A / spy)**(-1/n)
  md.materials.rheology_B = B * np.ones(md.mesh.numberofvertices)
  md.materials.rheology_n = n * np.ones(md.mesh.numberofelements)

While no-slip basal velocity boundary conditions are imposed, the :class:`~friction.friction` coefficient must be defined::
 
  md.friction.coefficient = np.ones(md.mesh.numberofvertices)
  md.friction.p           = np.ones(md.mesh.numberofelements)
  md.friction.q           = np.zeros(md.mesh.numberofelements)

Next, configure the model for "ice-sheet" boundary conditions via :class:`~SetIceSheetBC.SetIceSheetBC`, extrude vertically 5 cells in the :math:`z` direction with :func:`~model.model.extrude`, and set the appropriate "flow equation" with :class:`~setflowequation.setflowequation`::
 
  md = SetIceSheetBC(md)  # create placeholder arrays for indicies 
  md.extrude(6, 1.0)
  md = setflowequation(md, mdl_odr, 'all')

The basal-velocity-boundary conditions are then set within the :class:`~model.model` property :class:`~stressbalance.stressbalance`:: 
  	
  md.stressbalance.spcvx = np.nan * np.ones(md.mesh.numberofvertices)
  md.stressbalance.spcvy = np.nan * np.ones(md.mesh.numberofvertices)
  md.stressbalance.spcvz = np.nan * np.ones(md.mesh.numberofvertices)
  
  basal_v                         = md.mesh.vertexonbase
  md.stressbalance.spcvx[basal_v] = 0.0
  md.stressbalance.spcvy[basal_v] = 0.0
  md.stressbalance.spcvz[basal_v] = 0.0

The periodic-velocity-lateral-boundary conditions specified by the ISMIP HOM experiment are defined by pairing lateral nodes as follows:: 
  
  minX = np.where(md.mesh.x == 0)[0] + 1
  maxX = np.where(md.mesh.x == L)[0] + 1
  
  # for y, maxX and minX should be excluded :
  minY = np.where(np.logical_and(md.mesh.y == 0,
                                 md.mesh.x != L,
                                 md.mesh.x != 0))[0] + 1
  maxY = np.where(np.logical_and(md.mesh.y == L,
                                 md.mesh.x != L,
                                 md.mesh.x != 0))[0] + 1
  
  # set the nodes that should be paired together :
  md.stressbalance.vertex_pairing = np.array([np.append(minX, minY),
                                              np.append(maxX, maxY)]).T

Solve the momentum balance
--------------------------

Now, set up the computing environment variables using the :class:`~generic.generic` class, enable verbose solver output with :class:`~verbose.verbose`, and finally solve the system with the :class:`~solve.solve` class::
  
  md.cluster = generic('name', gethostname(), 'np', 1)
  md.verbose = verbose('convergence', True)
  md         = solve(md, 'Stressbalance')

Plot the results
----------------

TODO



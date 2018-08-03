import numpy         as np
from issm.model  import model

def vtuwrite(field, name, md, filename):
  """
  VTUWRITE - write a vtu file from a dictionary given in input

  Output to .vtu for viewing in paraview.

  Special thanks to Dr. Joel Brown's script at

    http://icewiki.umt.edu/index.php/ISSM_Python_assimilation

  """
  print('Creating .vtu file')
 
  fid       = open(filename,'w')              # vtu file to write to
  n_elem    = md.mesh.numberofelements        # number of elements
  n_vert    = md.mesh.numberofvertices        # number of verticies
  dim       = md.mesh.dimension()             # topological dimension
  n_vert_e  = np.shape(md.mesh.elements)[1]   # num vertices per element

  points    = np.array([md.mesh.x, md.mesh.y, md.mesh.z]).T  # coords 
  ISSMtypes = 5 * np.ones((n_elem, 1))                       # data type
  conn      = md.mesh.elements - 1                           # connectivity 
  off       = n_vert_e * np.arange(1, n_elem+1)              # element offset 

  # determine if these are vector data :
  if type(field) == tuple or type(field) == list:
    num_comp = len(field)
    pd_type  = 'Vectors="%s"' % name    
    vector   = True
  else:
    pd_type  = 'Scalars="%s"' % name    
    vector   = False

  # write the mesh data :
  fid.write('<?xml version="1.0"?>\n')
  fid.write('<VTKFile type="UnstructuredGrid" version="0.1">\n')
  fid.write('  <UnstructuredGrid>\n')
  fid.write('    <Piece NumberOfPoints="%i" NumberOfCells="%i">\n' \
            % (n_vert, n_elem))
  fid.write('      <Points>\n')
  fid.write('        <DataArray type="Float64"\n')
  fid.write('                   NumberOfComponents="%i"\n' % dim)
  fid.write('                   format="ascii">\n')
  points.tofile(fid, sep=" ", format="%f")
  fid.write('\n')
  fid.write('        </DataArray>\n')
  fid.write('      </Points>\n')
  fid.write('      <Cells>\n')
  fid.write('        <DataArray type="UInt32"\n')
  fid.write('                   Name="connectivity"\n')
  fid.write('                   format="ascii">\n')
  conn.tofile(fid, sep=" ", format="%s")
  fid.write('\n')
  fid.write('        </DataArray>\n')
  fid.write('        <DataArray type="UInt32" Name="offsets" format="ascii">\n')
  off.tofile(fid, sep=" ", format="%d")
  fid.write('\n')
  fid.write('        </DataArray>\n')
  fid.write('        <DataArray type="UInt32" Name="types" format="ascii">\n')
  ISSMtypes.tofile(fid, sep=" ", format="%d")
  fid.write('\n')
  fid.write('        </DataArray>\n')
  fid.write('      </Cells>\n')
  
  # write the data :
  fid.write('      <PointData %s>\n' % pd_type)
  fid.write('        <DataArray type="Float64"\n')
  fid.write('                   Name="%s"\n' % name)
  if vector:
    fid.write('                   NumberOfComponents="%s"\n' % num_comp)
  fid.write('                   format="ascii">\n')

  if vector:
    for f in np.vstack(field).T:
      f.tofile(fid, sep=" ", format="%f")
  else:
    field.tofile(fid, sep=" ", format="%f")

  fid.write('\n')
  fid.write('        </DataArray>\n')

  fid.write('      </PointData>\n')
  fid.write('    </Piece>\n')
  fid.write('  </UnstructuredGrid>\n')
  fid.write('</VTKFile>\n')
  fid.close()




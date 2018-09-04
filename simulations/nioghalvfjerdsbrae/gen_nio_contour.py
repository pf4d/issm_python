import cslvr as cs
import numpy as np
import os

#===============================================================================
# data preparation :
out_dir   = './dump/meshes/'
mesh_name = 'nioghalvfjerdsbrae'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# get the togography data :
bedmachine = cs.DataFactory.get_bedmachine()
dbm        = cs.DataInput(bedmachine)

#===============================================================================
# generate the contour :
m = cs.MeshGenerator(dbm, mesh_name, out_dir)

m.create_contour('mask', zero_cntr=0.001, skip_pts=8)
#m.create_contour('H', zero_cntr=100, skip_pts=20)   # 50 meter thick. contour
m.eliminate_intersections(dist=100)                  # eliminate problems

#===============================================================================
# a box region :
#x1 = -500000; y1 = -2190000
#x2 = -150000; y2 = -2320000
#
#new_cont = np.array([[x1, y1],
#                     [x2, y1],
#                     [x2, y2],
#                     [x1, y2],
#                     [x1, y1]])
#
#m.intersection(new_cont)

#===============================================================================
# or a basin :

gb = cs.GetBasin(dbm, basin='2.1')
gb.remove_skip_points(400)
gb.extend_edge(10000)
gb.intersection(m.longest_cont)
#gb.plot_xycoords(other=m.longest_cont)
m.set_contour(gb.get_xy_contour())

#===============================================================================
# process the file and extrude :

m.eliminate_intersections(dist=200)              # eliminate interscting lines
m.check_dist()                                   # remove points too close
m.write_argus_contour()                          # create a .exp contour file
m.close_file()                                   # close the files




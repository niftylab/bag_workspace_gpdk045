import numpy as np
import pprint
import laygo2
import laygo2.interface
import laygo2_tech as tech

# Parameter definitions #############
# Variables
cell_type = 'inv'
nf = 24
# Templates
tpmos_name = 'pmos'
tnmos_name = 'nmos'
# Grids
pg_name = 'placement_basic'
r12_name = 'routing_12_cmos'
r23_name = 'routing_23_cmos'
# Design hierarchy
libname = 'logic_generated'
cellname = cell_type+'_'+str(nf)+'x'
# End of parameter definitions ######

# Generation start ##################
# 1. Load templates and grids.
print("Load templates")
templates = tech.load_templates()
tpmos, tnmos = templates[tpmos_name], templates[tnmos_name]
print(templates[tpmos_name], templates[tnmos_name], sep="\n")

print("Load grids")
grids = tech.load_grids(templates=templates)
pg, r12, r23 = grids[pg_name], grids[r12_name], grids[r23_name]
print(grids[pg_name], grids[r12_name], grids[r23_name], sep="\n")

# 2. Create a design hierarchy
lib = laygo2.object.database.Library(name=libname)
dsn = laygo2.object.database.Design(name=cellname, libname=libname)
lib.append(dsn)

# 3. Create istances.
print("Create instances")
in0 = tnmos.generate(name='MN0', params={'nf': nf, 'tie': 'S'})#, 'bndl': True, 'bndr': True})
ip0 = tpmos.generate(name='MP0', transform='MX', params={'nf': nf, 'tie': 'S'})#, 'bndl': True, 'bndr': True})

# 4. Place instances.
dsn.place(grid=pg, inst=in0, mn=[0,0])
dsn.place(grid=pg, inst=ip0, mn=pg.mn.top_left(in0) + pg.mn.height_vec(ip0))

# 5. Create and place wires.
print("Create wires")
# IN
_mn = [r23.mn(in0.pins['G'])[0], r23.mn(ip0.pins['G'])[0]]
vin0, rin0, vin1 = dsn.route(grid=r23, mn=_mn, via_tag=[True, True])

# OUT
_mn = [r23.mn(in0.pins['D'])[0], r23.mn(ip0.pins['D'])[0]]
_track = [r23.mn(ip0.pins['D'])[1,0]-1, None]
vout0,rout0,vout1 = dsn.route_via_track(grid=r23, mn=_mn, track=_track)
'''
# Internal
_mn_n = []
_mn_p = []
init_point_n = r12.mn(in0.pins['D'])[0]
init_point_p = r12.mn(ip0.pins['D'])[0]
for i in range(int(nf/2)):
   _mn_n.append(init_point_n + np.array([2*i+1,1])) # create VIA1 for internal Drain connect
   _mn_p.append(init_point_p + np.array([2*i+1,1])) # Total nf/2 number of vias should be generated
#_mn_n = [r12.mn(in0.pins['D'])[0]+np.array([1,1]), r12 mn(in0.pins['D'])[1]+np.array([-1,1])]
#_mn_p = [r12.mn(ip0.pins['D'])[0]+np.array([1,1]), r12.mn(ip0.pins['D'])[1]+np.array([-1,1])]
#rint0 = dsn.route(grid=r12, mn=_mn_n, via_tag=[True, True, True, True, True, True])
#rint1 = dsn.route(grid=r12, mn=_mn_p, via_tag=[True, True, True, True, True, True])
rint0 = dsn.route(grid=r12, mn=_mn_n, via_tag=[True for i in range(len(_mn_n))])
rint1 = dsn.route(grid=r12, mn=_mn_p, via_tag=[True for i in range(len(_mn_p))])

# VSS
rvss0 = dsn.route(grid=r12, mn=[r12.mn(in0.pins['RAIL'])[0], r12.mn(in0.pins['RAIL'])[1]])

# VDD
rvdd0 = dsn.route(grid=r12, mn=[r12.mn(ip0.pins['RAIL'])[0], r12.mn(ip0.pins['RAIL'])[1]])

# 6. Create pins.
pin0 = dsn.pin(name='IN', grid=r23, mn=r23.mn.bbox(rin0))
pout0 = dsn.pin(name='OUT', grid=r23, mn=r23.mn.bbox(rout0))
pvss0 = dsn.pin(name='VSS', grid=r12, mn=r12.mn.bbox(rvss0))
pvdd0 = dsn.pin(name='VDD', grid=r12, mn=r12.mn.bbox(rvdd0))
'''
# 7. Export to physical database.
print("Export design")

# Uncomment for BAG export
laygo2.interface.bag.export(lib, filename=libname+'_'+cellname+'.il', cellname=None, scale=1e-3, reset_library=False, tech_library=tech.name)

# 8. Export to a template database file.
nat_temp = dsn.export_to_template()
laygo2.interface.yaml.export_template(nat_temp, filename=libname+'_templates.yaml', mode='append')

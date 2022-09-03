##########################################################
#                                                        #
#                Inverter Layout Generator               #
#     Contributors: T. Shin, S. Park, Y. Oh, T. Kang     #
#                 Last Update: 2022-09-02                #
#                                                        #
##########################################################

import numpy as np
import pprint
import laygo2
import laygo2.interface
import laygo2_tech as tech

# Parameter definitions #############
# Design Variables
nf = 6

# Templates
tpmos_name = 'pmos'
tnmos_name = 'nmos'

# Grids
pg_name = 'placement_basic'
r12_name = 'routing_12_cmos'
r23_name = 'routing_23_cmos'
r34_name = 'routing_34_basic'

# Design hierarchy
libname = 'logic_generated'
cellname = 'inv_'+str(nf)+'x'
# End of parameter definitions ######

# Generation start ##################
# 1. Load templates and grids.
print("Load templates")
templates = tech.load_templates()
tpmos, tnmos = templates[tpmos_name], templates[tnmos_name]
### Uncomment if you want to print templates information.
# print(templates[tpmos_name], templates[tnmos_name], sep="\n") 

print("Load grids")
grids = tech.load_grids(templates=templates)
pg, r12, r23, r34 = grids[pg_name], grids[r12_name], grids[r23_name], grids[r34_name]
### Uncomment if you want to print grids information.
# print(grids[pg_name], grids[r12_name], grids[r23_name], grids[r34_name], sep="\n") 

print('--------------------')
print('Now Creating '+cellname)
      
# 2. Create a design hierarchy
lib = laygo2.object.database.Library(name=libname)
dsn = laygo2.object.database.Design(name=cellname, libname=libname)
lib.append(dsn)
      
# 3. Create instances.
print("Create instances")
in0 = tnmos.generate(name='MN0',                 params={'nf': nf, 'tie': 'S'})
ip0 = tpmos.generate(name='MP0', transform='MX', params={'nf': nf,'tie': 'S'})

# 4. Place instances.
dsn.place(grid=pg, inst=in0, mn=[0,0])
dsn.place(grid=pg, inst=ip0, mn=pg.mn.top_left(in0) + pg.mn.height_vec(ip0))
### Or the instance placement can be described with a two-dimesional list.
# dsn.place(grid=pg, inst=[[in0], [ip0]], mn=[0,0])

# 5. Create and place wires.
print("Create wires")

# IN
_mn = [r23.mn(in0.pins['G'])[0], r23.mn(ip0.pins['G'])[0]]
_track = [r23.mn(in0.pins['G'])[0,0]-1, None]
rin0 = dsn.route_via_track(grid=r23, mn=_mn, track=_track)

# OUT
_mn = [r23.mn(in0.pins['D'])[1], r23.mn(ip0.pins['D'])[1]]
vout0, rout0, vout1 = dsn.route(grid=r23, mn=_mn, via_tag=[True, True])

# VSS
rvss0 = dsn.route(grid=r12, mn=[r12.mn(in0.pins['RAIL'])[0], r12.mn(in0.pins['RAIL'])[1]])

# VDD
rvdd0 = dsn.route(grid=r12, mn=[r12.mn(ip0.pins['RAIL'])[0], r12.mn(ip0.pins['RAIL'])[1]])
      
# 6. Create pins.
pin0 = dsn.pin(name='I', grid=r23, mn=r23.mn.bbox(rin0[2]))
pout0 = dsn.pin(name='O', grid=r23, mn=r23.mn.bbox(rout0))
pvss0 = dsn.pin(name='VSS', grid=r12, mn=r12.mn.bbox(rvss0))
pvdd0 = dsn.pin(name='VDD', grid=r12, mn=r12.mn.bbox(rvdd0))

# 7. Export to physical database.
print("Export design")
print("")
laygo2.interface.bag.export(lib, filename=cellname+'.il', cellname=None, scale=1e-3, reset_library=False, tech_library=tech.name)
### Filename example: ./laygo2_generators_private/logic/skill/logic_generated_inv_hs_2x.il
      
# 8. Export to a template database file.
nat_temp = dsn.export_to_template()
laygo2.interface.yaml.export_template(nat_temp, filename=libname+'_templates.yaml', mode='append')
### Filename example: ./laygo2_generators_private/logic/logic_generated_templates.yaml



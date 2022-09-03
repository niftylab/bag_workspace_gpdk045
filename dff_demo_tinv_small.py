##########################################################
#                                                        #
#  Tri-State Inverter with small size Layout Gernerator  #
#     Contributors: T. Shin, S. Park, Y. Oh, T. Kang     #
#                 Last Update: 2022-05-27                #
#                                                        #
##########################################################

import numpy as np
import pprint
import laygo2
import laygo2.interface
import laygo2_tech as tech

# Parameter definitions #############
# Design Variables
cell_type = 'tinv_small'
nf = 1

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
# End of parameter definitions ######

# Generation start ##################
# 1. Load templates and grids.
print("Load templates")
templates = tech.load_templates()
tpmos, tnmos = templates[tpmos_name], templates[tnmos_name]
# tlib = laygo2.interface.yaml.import_template(filename=export_path+'logic_generated_templates.yaml') # Uncomment if you use the logic templates
# print(templates[tpmos_name], templates[tnmos_name], sep="\n") # Uncomment if you want to print templates

print("Load grids")
grids = tech.load_grids(templates=templates)
pg, r12, r23, r34 = grids[pg_name], grids[r12_name], grids[r23_name], grids[r34_name]
# print(grids[pg_name], grids[r12_name], grids[r23_name], grids[r34_name], sep="\n") # Uncomment if you want to print grids

cellname = cell_type+'_'+str(nf)+'x'
print('--------------------')
print('Now Creating '+cellname)

# 2. Create a design hierarchy
lib = laygo2.object.database.Library(name=libname)
dsn = laygo2.object.database.Design(name=cellname, libname=libname)
lib.append(dsn)

# 3. Create istances.
print("Create instances")
nstack = templates['nmos4_fast_center_2stack'].generate(name='nstack')
nbndl = templates['nmos4_fast_boundary'].generate(name='nbndl')
nbndr = templates['nmos4_fast_boundary'].generate(name='nbndr')
nspace0 = templates['nmos4_fast_space'].generate(name='nspace0')
nspace1 = templates['nmos4_fast_space'].generate(name='nspace1')
pstack = templates['pmos4_fast_center_2stack'].generate(name='pstack', transform='MX')
pbndl = templates['pmos4_fast_boundary'].generate(name='pbndl', transform='MX')
pbndr = templates['pmos4_fast_boundary'].generate(name='pbndr', transform='MX')
pspace0 = templates['pmos4_fast_space'].generate(name='pspace0', transform='MX')
pspace1 = templates['pmos4_fast_space'].generate(name='pspace1', transform='MX')

# 4. Place instances.
dsn.place(grid=pg, inst=nbndl,   mn=[0,0])
dsn.place(grid=pg, inst=nstack,  mn=pg.mn.bottom_right(nbndl))
dsn.place(grid=pg, inst=nbndr,   mn=pg.mn.bottom_right(nstack))
dsn.place(grid=pg, inst=nspace0, mn=pg.mn.bottom_right(nbndr))
dsn.place(grid=pg, inst=nspace1, mn=pg.mn.bottom_right(nspace0))
dsn.place(grid=pg, inst=pbndl,   mn=pg.mn.top_left(nbndl)+pg.mn.height_vec(pbndl))
dsn.place(grid=pg, inst=pstack,  mn=pg.mn.top_right(pbndl))
dsn.place(grid=pg, inst=pbndr,   mn=pg.mn.top_right(pstack))
dsn.place(grid=pg, inst=pspace0, mn=pg.mn.top_right(pbndr))
dsn.place(grid=pg, inst=pspace1, mn=pg.mn.top_right(pspace0))

# 5. Create and place wires.
print("Create wires")

# IN
_mn = [r12.mn(nstack.pins['G0'])[0], r12.mn(pstack.pins['G0'])[0]]
rin0 = dsn.route(grid=r23, mn=_mn)

_mn = [r12.mn(nstack.pins['G0'])[0], r12.mn(pstack.pins['G0'])[0]]
dsn.route(grid=r12, mn=_mn)

_mn = [np.mean(r23.mn.bbox(rin0), axis=0, dtype=np.int), np.mean(r23.mn.bbox(rin0), axis=0, dtype=np.int)+[2,0]]
dsn.route(grid=r23, mn=_mn, via_tag=[True, False])
dsn.via(grid=r12, mn=np.mean(r23.mn.bbox(rin0), axis=0, dtype=np.int))

# OUT
_mn = [r23.mn(nstack.pins['D0'])[0], r23.mn(pstack.pins['D0'])[1]]
vout0, rout0, vout1 = dsn.route(grid=r23, mn=_mn, via_tag=[True, True])

vint0 = dsn.via(grid=r12, mn=r23.mn(nstack.pins['D0'])[0])
vint1 = dsn.via(grid=r12, mn=r23.mn(pstack.pins['D0'])[1])

# EN
_mn = [r23.mn(nstack.pins['G1'])[0], r23.mn(nstack.pins['G1'])[0]+[1,0]]
ren0, ven0 = dsn.route(grid=r23, mn=_mn, via_tag=[False, True])

ven1 = dsn.via(grid=r12, mn=r12.mn(nstack.pins['G1'])[0])
_mn = [r23.mn(nstack.pins['G1'])[0]+[1,0], r23.mn(pstack.pins['G1'])[0]+[1,0]]
ren1 = dsn.route(grid=r23, mn=_mn)

# ENB
_mn = [r23.mn(pstack.pins['G1'])[0], r23.mn(pstack.pins['G1'])[0]+[-1,0]]
renb0, venb0 = dsn.route(grid=r23, mn=_mn, via_tag=[False, True])

venb1 = dsn.via(grid=r12, mn=r12.mn(pstack.pins['G1'])[0])
_mn = [r23.mn(pstack.pins['G1'])[0]+[-1,0], r23.mn(nstack.pins['G1'])[0]+[-1,0]]
renb1 = dsn.route(grid=r23, mn=_mn)

# VSS  
_mn = [r12.mn.bottom_left(nbndl), r12.mn.bottom_right(nspace1)]
rvss0 = dsn.route(grid=r12, mn=_mn)

_mn = [r12.mn(nstack.pins['S0'])[0], r12.mn(nstack.pins['S0'])[0]+[0,-1]]
rvss1, _ = dsn.route(grid=r12, mn=_mn, via_tag=[False, True])

# VDD
_mn = [r12.mn.top_left(pbndl), r12.mn.top_right(pspace1)]
rvdd0 = dsn.route(grid=r12, mn=_mn)

_mn = [r12.mn(pstack.pins['S0'])[1], r12.mn(rvdd0)[0]+[1,0]]
rvdd1 = dsn.route(grid=r12, mn=_mn, via_tag=[False, True])

################################ ADDED FOR DRC ################################
_mn = [r23.mn(nstack.pins['D0'])[0], r23.mn(nstack.pins['D0'])[0]+[-2,0]]
dsn.route(grid=r23, mn=_mn)
_mn = [r23.mn(pstack.pins['D0'])[1], r23.mn(pstack.pins['D0'])[1]+[-2,0]]
dsn.route(grid=r23, mn=_mn)
_mn = [r23.mn(nstack.pins['G1'])[0], r23.mn(nstack.pins['G1'])[0]+[2,0]]
dsn.route(grid=r23, mn=_mn)
_mn = [r23.mn(pstack.pins['G1'])[0], r23.mn(pstack.pins['G1'])[0]+[2,0]]
dsn.route(grid=r23, mn=_mn)
############################## LINES FOR DRC END ##############################

# 6. Create pins.
pin0 = dsn.pin(name='I', grid=r23, mn=r23.mn.bbox(rin0))
pout0 = dsn.pin(name='O', grid=r23, mn=r23.mn.bbox(rout0))
pen0 = dsn.pin(name='EN', grid=r23, mn=r23.mn.bbox(ren1))
penb0 = dsn.pin(name='ENB', grid=r23, mn=r23.mn.bbox(renb1))
pvss0 = dsn.pin(name='VSS', grid=r12, mn=r12.bbox(rvss0))
pvdd0 = dsn.pin(name='VDD', grid=r12, mn=r12.bbox(rvdd0))

# 7. Export to physical database.
print("Export design")
print("")
laygo2.interface.bag.export(lib, filename=libname+'_'+cellname+'.il', cellname=None, scale=1e-3, reset_library=False, tech_library=tech.name)
# Filename example: ./laygo2_generators_private/logic/skill/logic_generated_tinv_small_1x.il

# 8. Export to a template database file.
nat_temp = dsn.export_to_template()
laygo2.interface.yaml.export_template(nat_temp, filename=libname+'_templates.yaml', mode='append')
# Filename example: ./laygo2_generators_private/logic/logic_generated_templates.yaml

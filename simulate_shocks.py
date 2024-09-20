
import sys
import os
import irispie as ir


m = ir.Simultaneous.from_pickle_file("model.pkl", )

start_sim = ir.ii(1)
end_sim = ir.ii(5)
sim_span = start_sim >> end_sim

d0 = ir.Databox.steady(m, sim_span, )

# d1 = d0.copy()
# d1["shk_y_gap"][start_sim>>start_sim+1] = (1, 2, )
# s1, info1 = m.simulate(d1, sim_span, return_info=True, )
# 
# d2 = d0.copy()
# d2["shk_y_gap"][start_sim>>start_sim+1] = (1, 2, )
# d2["ant_shk_y_gap"][start_sim>>start_sim+1] = (-1, -2, )
# s2, info2 = m.simulate(d2, sim_span, return_info=True, )

p3 = ir.SimulationPlan(m, sim_span, )
p3.swap_anticipated(start_sim+1, ("y_gap", "ant_shk_y_gap", ))
p3.swap_unanticipated(start_sim+3, ("y_gap", "shk_y_gap", ))

d3 = d0.copy()
d3["shk_y_gap"].alter_num_variants(2, )
d3["shk_y_gap"][start_sim>>start_sim+1] = [(0, 1, ), (0, 0, )]

d3["y_gap"][start_sim+1] = -1
d3["y_gap"][start_sim+3] = 2

s3, info3 = m.simulate(d3, sim_span, plan=p3, return_info=True, num_variants=2, )
f00 = info3[0]["frame_databoxes"][0]
f01 = info3[0]["frame_databoxes"][1]
f11 = info3[1]["frame_databoxes"][0]
f = ir.Databox.merged((f00, f01, f11, ))

d4 = d3.copy()
p4 = p3.copy()

s4, info4 = m.simulate(
    d4, sim_span,
    plan=p4,
    method="stacked_time",
    return_info=True,
    num_variants=2,
    solver_settings={"step_tolerance": float("inf"), },
    when_fails="warning",
)


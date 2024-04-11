
# Short example of a linear gap model


import irispie as ir
import sys
import re
import json

import create_model

# ir.min_irispie_version_required("0.22.1", )


## Create model object

m = create_model.main()


## Print steady state

print(m.get_steady_levels(round=4, ))


## Calculate first-order solution matrices

m.solve(clip_small=False, )
sol = m._variants[0].solution


c, dimn = m.get_acov()
print(dimn.select(c[0], ["y_gap", "diff_cpi", "cpi"]))


c, dn = m.get_acov(up_to_order=4, )
r, dn = m.get_acorr(acov=c, )

var = m._variants[0]
sol = m._variants[0].solution
cov_u = m.get_cov_unanticipated_shocks()


#from irispie.fords import initializers as iz
#ia, ib = iz.initialize(sol, cov_u, )


## Run shock simulation

start_sim = ir.ii(1)
sim_horizon = 40
end_sim = start_sim + sim_horizon - 1
sim_range = start_sim >> end_sim

deviation = True
ss_db = ir.Databox.steady(m, sim_range, deviation=deviation, )

in_db = ss_db.copy()

in_db["ant_shk_y_gap"].alter_num_variants(2, )
in_db["ant_shk_y_gap"][start_sim+5>>start_sim+8] = [(1, 1.5, 0.5, 0.2), 0]

in_db["shk_y_gap"].alter_num_variants(2, )
in_db["shk_y_gap"][start_sim+5>>start_sim+8] = [0, (1, 1.5, 0.5, 0.2)]

sim_db, *_ = m.simulate(in_db, sim_range, deviation=deviation, num_variants=2, )


## Plot results

sim_ch = ir.Chartpack(
    span=start_sim-1>>end_sim,
    highlight=start_sim>>start_sim+3,
    legend=["Anticipated", "Unanticipated"],
)

fig = sim_ch.add_figure("Anticipated vs unanticipated", )

fig.add_charts((
    "Output gap: y_gap",
    "Inflation Q/Q: diff_cpi",
    "Interest rate: rs",
    "Anticipated output gap shocks: ant_shk_y_gap",
    "Unanticipated output gap shocks: shk_y_gap",
))

sim_ch.plot(sim_db, )


#---------------------------------------------------------------------------------


## Load data from a CSV file

fred_db = ir.Databox.from_sheet(
    "fred_data.csv",
    description_row=True,
    databox_settings=dict(description="US macro data from FRED", ),
    date_creator=ir.Dater.from_iso_string,
)


## Preprocess data

fred_db["cpi"] = 100*ir.log(fred_db["CPI"])
fred_db["diff_cpi"] = 4*ir.diff(fred_db["cpi"])
fred_db["diff4_cpi"] = ir.diff(fred_db["cpi"], -4)

fred_db["y"] = 100*ir.log(fred_db["GDPC"])
fred_db["y_tnd"], fred_db["y_gap"] = ir.hpf(fred_db["y"], )

fred_db["rs"] = fred_db["TB3M"]

print(fred_db)


## Plot historical data

plot_range = ir.qq(2010,1)>>ir.qq(2022,4)


hist_ch = ir.Chartpack(
    span=plot_range,
)

fig = hist_ch.add_figure("Historical data", )

fig.add_charts((
    "Output | Potential output: y | y_tnd",
    "Output gap: y_gap",
    "Inflation Q/Q | Y/Y: diff_cpi | diff4_cpi",
    "Interest rate: rs",
))

hist_ch.plot(fred_db, )


#---------------------------------------------------------------------------------


## Run a forecast

start_fcast = ir.qq(2021,3)
end_fcast = ir.qq(2026,4)
fcast_range = start_fcast >> end_fcast

fred_db["shk_diff_cpi"] = ir.Series()
#fred_db["shk_diff_cpi"][start_fcast+4] = -2

print("Necessary initial conditions")
for i in m.get_initials(): print(i)

mm = m.copy()
mm.alter_num_variants(2)

p = ir.SimulationPlan(mm, fcast_range, )
p.swap_unanticipated(fcast_range[0], ("y_gap", "shk_y_gap", ), )

mm[1].assign(c0_diff_cpi=0.8, )
mm[1].solve()

fcast_db, *_ = mm.simulate(fred_db, fcast_range, )

fcast_ch = sim_ch.copy()
fcast_ch.span = start_fcast-30*4 >> end_fcast
fcast_ch.highlight = start_fcast >> end_fcast
fcast_ch.plot(fcast_db, )


## Save results to a CSV file

fcast_db.to_sheet(
    "forecast_output_databank.csv",
    frequency_span={ir.QUARTERLY: ir.qq(2000,1)>>fcast_range[-1], },
)

from irispie import frames

sim_span = ir.qq(2020,1, ..., 2023,4)

p = ir.SimulationPlan(m, sim_span, )
p.swap_unanticipated(sim_span[1], ("y_gap", "shk_y_gap", ), )

test = ir.Databox()
test["shk_y_gap"] = ir.Series(dates=(ir.qq(2020,1),ir.qq(2021,2), ), values=(1, 1), )

slatable = m.get_slatable(shocks_from_data=True, )
ds = ir.Dataslate.from_databox_for_slatable(
    slatable, test, sim_span,
)

x = frames.split_into_frames(m, ds, p, )



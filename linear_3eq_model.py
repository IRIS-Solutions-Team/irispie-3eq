
# Short example of a linear gap model


import irispie as ir
import sys
import re
import json

# ir.min_irispie_version_required("0.22.1", )


## Create model object

m = ir.Simultaneous.from_file("linear_3eq.model", linear=True, )

with open("linear_3eq.model", "rt") as f:
    x = f.read()

x = re.sub(r"\[(.\d+)\]", r"{\1}", x)
x = x.replace("unanticipated-", "")
x = x.replace("anticipated-", "")
x = x.replace("#", "%", )

with open("linear_3eq.matlab", "wt+") as f:
    f.write(x)


## Assign parameters

parameters = dict(
    ss_rrs = 0.5,
    ss_diff_cpi = 2,
    ss_diff_y_tnd = 1.5,
    c0_y_gap = 0.75,
    c1_y_gap = 0.10,
    c0_diff_cpi = 0.55,
    c1_diff_cpi = 0.10,
    c1_E_diff_cpi = 1,
    c0_rs = 0.75,
    c1_rs = 4,
    std_shk_y_tnd = 1.0,
    std_shk_y_gap = 1.0,
    std_shk_diff_cpi = 1.0,
    std_shk_rs = 1.0,
)

with open("parameters.json", "wt+") as f:
    json.dump(parameters, f, indent=4, )

m.assign(parameters, )


## Calculate steady state

m.steady()

chk = m.check_steady()

print(m.get_steady_levels(round=4, ))


## Calculate first-order solution matrices

m.solve(clip_small=False, )
sol = m._variants[0].solution

ir.save(m, "linear_3eq.dill", )

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
in_db["ant_shk_y_gap"][start_sim>>start_sim+3] = [(1, 1.5, 0.5, 0.2), 0]

in_db["shk_y_gap"].alter_num_variants(2, )
in_db["shk_y_gap"][start_sim>>start_sim+3] = [0, (1, 1.5, 0.5, 0.2)]

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
    description="US macro data from FRED",
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

p = ir.PlanSimulate(mm, fcast_range)
p.swap(fcast_range[0], ("y_gap", "shk_y_gap"))

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


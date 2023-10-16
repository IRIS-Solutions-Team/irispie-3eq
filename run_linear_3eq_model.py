
# Short example of a linear gap model


from pprint import pprint
import irispie as _ir
import plotly as _pl


## Create model object

m = _ir.Model.from_file("linear_3eq.model", linear=True, )


## Assign parameters

m.assign(
    ss_rrs = 0.5,
    ss_diff_cpi = 2,
    c0_y_gap = 0.75,
    c1_y_gap = 0.10,
    c0_diff_cpi = 0.55,
    c1_diff_cpi = 0.10,
    c0_rs = 0.75,
    c1_rs = 4,
)

## Calculate steady state

m.steady()

chk = m.check_steady()

print(m.get_steady_levels(round=4, ))


## Calculate first-order solution matrices

m.solve()



## Run shock simulation

start_sim = _ir.ii(1)
sim_horizon = 40
end_sim = start_sim + sim_horizon - 1
sim_range = start_sim >> end_sim

deviation = True
ss_db = _ir.Databox.steady(m, sim_range, deviation=deviation, )

in_db = ss_db.copy()

in_db["shk_y_gap"][start_sim>>start_sim+3] = [1, 1.5, 0.5, 0.2]

out_db, *_ = m.simulate(in_db, sim_range, deviation=deviation, )


## Plot results

fig = _pl.subplots.make_subplots(
    rows=2, cols=2,
    subplot_titles=["Output gap", "Inflation Q/Q PA", "Interest rate", "Output gap shocks"]
)

out_db["y_gap"]     .plot(subplot=0, figure=fig)
out_db["diff_cpi"]  .plot(subplot=1, figure=fig)
out_db["rs"]        .plot(subplot=2, figure=fig)
out_db["shk_y_gap"] .plot(subplot=3, figure=fig, xline=start_sim-1, )

fig.show()


#################################################################################


## Load data from a CSV file

fred_db = _ir.Databox.from_sheet(
    "fred_data.csv",
    description_row=True,
    description="US macro data from FRED",
)


## Preprocess data

fred_db["cpi"] = 100*_ir.log(fred_db["CPI"])
fred_db["diff_cpi"] = 4*_ir.diff(fred_db["cpi"])
fred_db["diff4_cpi"] = _ir.diff(fred_db["cpi"], -4)

fred_db["y"] = 100*_ir.log(fred_db["GDPC"])
fred_db["y_tnd"], fred_db["y_gap"] = _ir.hpf(fred_db["y"], )

fred_db["rs"] = fred_db["TB3M"]

print(fred_db)


## Plot historical data

plot_range = _ir.qq(2010,1)>>_ir.qq(2022,4)

fig = _pl.subplots.make_subplots(
    rows=2, cols=2,
    subplot_titles=["Output | Potential output", "Output gap", "Inflation Q/Q PA | Y/Y", "Interest rate"],
)

(fred_db["y"] | fred_db["y_tnd"])            .plot(subplot=0, figure=fig, range=plot_range)
fred_db["y_gap"]                             .plot(subplot=1, figure=fig, range=plot_range)
(fred_db["diff_cpi"] | fred_db["diff4_cpi"]) .plot(subplot=2, figure=fig, range=plot_range)
fred_db["rs"]                                .plot(subplot=3, figure=fig, range=plot_range)

fig.show()


#################################################################################


## Run a forecast

start_fcast = _ir.qq(2021,3)
end_fcast = _ir.qq(2026,4)
fcast_range = start_fcast >> end_fcast

fred_db["shk_diff_cpi"] = _ir.Series()
#fred_db["shk_diff_cpi"][start_fcast+4] = -2

print("Necessary initial conditions")
pprint(m.get_initials())

mm = m.copy()
mm.alter_num_variants(2)

mm[1].assign(c0_diff_cpi=0.8, )
mm[1].solve()

fcast_db, *_ = mm.simulate(fred_db, fcast_range, )

fig = _pl.subplots.make_subplots(
    rows=2, cols=2,
    subplot_titles=["Output gap", "Inflation Q/Q PA", "Interest rate", "Output gap shocks"]
)

fcast_db["y_gap"]      .plot(subplot=0, figure=fig)
fcast_db["diff_cpi"]   .plot(subplot=1, figure=fig)
fcast_db["rs"]         .plot(subplot=2, figure=fig)
fcast_db["shk_y_gap"]  .plot(subplot=3, figure=fig, xline=fcast_range[0]-1, )

fig.show()


## Save results to a CSV file

fcast_db.to_sheet(
    "forecast_output_databank.csv", 
    frequency_range={_ir.Freq.QUARTERLY: _ir.qq(2000,1)>>fcast_range[-1], },
)



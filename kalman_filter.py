
import sys
import numpy as np
import irispie as ir
import wlogging as wl

import create_model


logger = wl.get_colored_logger("kalman_filter", level=wl.DEBUG, )


m = create_model.main()

logger.info("Parameter values")
print(m.get_parameters())

logger.info("Standard deviations of shocks")
print(m.get_stds())


start_sim = ir.qq(2021,1)
end_sim = ir.qq(2022,4)
sim_span = start_sim >> end_sim


obs_db = ir.Databox.from_sheet(
    "obs_db.csv",
    date_creator=ir.Dater.from_iso_string,
)

start_filt = start_sim
end_filt = end_sim
filt_span = start_filt >> end_filt
obs_db.clip(new_start_date=filt_span.start_date, )

# m.assign(
    # std_shk_y_tnd = 1,
    # std_shk_y_gap = 1,
    # std_shk_diff_cpi = 1,
    # std_shk_rs = 1,
    # std_shk_E_diff_cpi = 1,
# )

m.solve()

obs_db = ir.Databox()
# obs_db["obs_cpi"] = ir.Series(start_date=start_filt+2, values=(0, ), )
# obs_db["obs_diff_cpi"] = ir.Series(start_date=start_filt+2, values=(0, 0, ), )

# obs_db["std_shk_E_diff_cpi"] = ir.Series(
    # dates=start_filt+2>>start_filt+5,
    # values=0.222,
# )

#
# Experiment with different options
#

# out1, info1 = m.kalman_filter(obs_db, filt_span, )
# out2, info2 = m.kalman_filter(obs_db, filt_span, rescale_variance=True, )
# out3, info3 = m.kalman_filter(obs_db, filt_span, diffuse_factor=1e8, )
# out4, info4 = m.kalman_filter(obs_db, filt_span, return_predict=False, )


#
# Start the filter at a date sufficiently before the first observation
# so that the smoothed initial conditions and shocks can be resimulated
# on the same span as the original observations
#

ext_filt_span = start_filt + m.max_lag >> end_filt
# ext_filt_span = start_filt >> start_filt + 4
# obs_db["std_shk_E_diff_cpi"] = ir.Series(dates=start_filt+2>>start_filt+5, values=0.222)

obs_db["obs_y"] = ir.Series(start_date=start_filt+3, values=(0,), )
obs_db["obs_diff_y"] = ir.Series(start_date=start_filt+4, values=(0,), )
# obs_db["std_shk_y_tnd"] = ir.Series(dates=start_filt+4, values=10, )
obs_db["shk_y_gap"] = ir.Series(dates=start_filt+2, values=10, )
obs_db["ant_shk_y_gap"] = ir.Series(dates=start_filt+2, values=10, )

out, kinfo = m.kalman_filter(
    obs_db, filt_span,
    diffuse_factor=1e8,
    stds_from_data=True,
    shocks_from_data=True,
    prepend_initial=True,
)


# out.smooth_med('y_tnd | y | obs_y').plot()
# out.smooth_med['y_gap'].plot()

logger.info("Prediction step for y_tnd | y_gap")
print(out.predict_med("y_tnd | y_gap"))

logger.info("Smoothing step for y_tnd | y_gap | y_tnd+y_gap | obs_y")
print(out.smooth_med("y_tnd | y_gap | y_tnd+y_gap | obs_y"))

logger.info("Smoothing step for cpi")
#print(out.smooth_med["cpi"] | obs_db["obs_cpi"])


#
# Resimulate the model using the smoothed initial conditions and shocks
#

sim_db, sinfo = m.simulate(out.smooth_med, filt_span, )


#
# Compare transition variables from the smoother and from the simulation
#

variable_names = m.get_names(kind=ir.TRANSITION_VARIABLE, )

max_abs = lambda x: np.max(np.abs(x))

compare_db = ir.Databox()
for n in variable_names:
    diff = out.smooth_med[n] - sim_db[n]
    compare_db[n] = diff.apply(max_abs, ) if diff else None


logger.info("Max absolute difference between smoother and simulation")
print(compare_db)



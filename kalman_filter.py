
import numpy as np
import irispie as ir


model = ir.load("linear_3eq.dill", )

model.assign(
    ss_diff_y_tnd=0,
)

model.steady()
model.solve()
model.check_steady()

start_filt = ir.qq(2021,1)
end_filt = ir.qq(2022,4)
filt_span = start_filt >> end_filt

obs_db = ir.Databox()
values = (1.20, 1.03, 0.91, 1.97, 0.32, 0.91, 1.41, 1.48)
obs_db["obs_y"] = ir.Series(start_date=start_filt, values=values, )
obs_db["obs_cpi"] = ir.Series(start_date=start_filt, values=(10, None, 12, ), )

out1, info1 = model.kalman_filter(obs_db, filt_span, )
out2, info2 = model.kalman_filter(obs_db, filt_span, rescale_variance=True, )
out3, info3 = model.kalman_filter(obs_db, filt_span, diffuse_factor=1e8, )
out4, info4 = model.kalman_filter(obs_db, filt_span, return_predict=False, )





ext_filt_span = start_filt + model.max_lag >> end_filt
out, info = model.kalman_filter(obs_db, ext_filt_span, )

sim_db, *_ = model.simulate(out["smooth_mean"], filt_span, )



#
# Compare transition variables from the smoother and from the simulation
#

variable_names = model.get_names(kind=ir.TRANSITION_VARIABLE, )

max_abs = lambda x: np.max(np.abs(x))

compare_db = ir.Databox()
for n in variable_names:
    diff = out["smooth_mean"][n] - sim_db[n]
    compare_db[n] = diff.apply(max_abs, ) if diff else None



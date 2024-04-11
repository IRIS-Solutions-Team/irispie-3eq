
import sys
import numpy as np
import json as js
import irispie as ir
import wlogging as wl

import create_model


logger = wl.get_colored_logger("kalman_filter", level=wl.DEBUG, )


m = create_model.main()


logger.info("Parameter values")
print(m.get_parameters())

logger.info("Standard deviations of shocks")
print(m.get_stds())


logger.info("Reading databox with observations and shock assumptions")
obs_db = ir.Databox.from_sheet(
    "data_files/obs_db.csv",
    description_row=False,
    date_creator=ir.Period.from_iso_string,
)

logger.info("Reading dates")
with open("data_files/dates.json", "rt") as f:
    dates = js.load(f, )

start_filt = ir.Period.from_iso_string(ir.QUARTERLY, dates["start_filt"], )
end_filt = ir.Period.from_iso_string(ir.QUARTERLY, dates["end_filt"], )
filt_span = start_filt >> end_filt

out1, info1 = m.kalman_filter(
    obs_db, filt_span,
    diffuse_factor=1e8,
    stds_from_data=False,
    shocks_from_data=False,
    prepend_initial=True,
)

s1 = out1.smooth_med
t1 = out1.smooth_std

out2, info2 = m.kalman_filter(
    obs_db, filt_span,
    diffuse_factor=1e8,
    stds_from_data=True,
    shocks_from_data=True,
    prepend_initial=True,
)

s2 = out2.smooth_med.copy()
s2.keep(m.get_names(kind=ir.TRANSITION_VARIABLE, ))

t2 = out2.smooth_std.copy()
t2.keep(m.get_names(kind=ir.TRANSITION_VARIABLE, ))


logger.info("Writing smooth medians to csv")
s2.to_sheet(
    "data_files/python_smooth_med.csv",
    description_row=False,
    date_formatter=ir.Period.to_iso_string,
)

logger.info("Writing smooth stds to csv")
t2.to_sheet(
    "data_files/python_smooth_std.csv",
    description_row=False,
    date_formatter=ir.Period.to_iso_string,
)


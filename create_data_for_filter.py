
import irispie as ir
import numpy as np
import json as js


np.random.seed(0)


fred_db = ir.Databox.from_sheet(
    "data_files/fred_data.csv",
    description_row=True,
    date_creator=ir.Dater.from_iso_string,
)

fred_db["y"] = 100*ir.log(fred_db["GDPC"])
fred_db["diff_y"] = 4*ir.diff(fred_db["y"])
fred_db["cpi"] = 100*ir.log(fred_db["CPI"])
fred_db["diff_cpi"] = 4*ir.diff(fred_db["cpi"])

start_filt = ir.qq(2015,1)
end_filt = ir.qq(2022,4)

filt_span = start_filt >> end_filt

obs_db = ir.Databox(
    obs_diff_y=fred_db["diff_y"],
    obs_y=fred_db["y"](start_filt),
    obs_diff_cpi=fred_db["diff_cpi"],
    obs_cpi=fred_db["cpi"](start_filt),
    std_shk_y_gap=ir.Series(periods=filt_span, values=0.5+np.random.uniform(size=len(filt_span)), ),
    std_shk_diff_cpi=ir.Series(periods=filt_span, values=1.5+np.random.uniform(size=len(filt_span)), ),
    shk_y_gap=ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), ),
    shk_diff_cpi=ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), ),
)

obs_db.clip(start_filt, end_filt, )
obs_db.apply(lambda x: x.round(6), )


obs_db.to_sheet("data_files/obs_db.csv", date_formatter=ir.Dater.to_iso_string, )


dates = {
    "start_filt": start_filt.to_iso_string(),
    "end_filt": end_filt.to_iso_string(), 
}
with open("data_files/dates.json", "wt+") as f:
    js.dump(dates, f, indent=4, )



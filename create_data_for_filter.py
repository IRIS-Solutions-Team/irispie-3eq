
import irispie as ir
import numpy as np
import json as js


np.random.seed(0)


fred_db = ir.Databox.from_csv(
    "data_files/fred_data.csv",
    description_row=True,
    date_creator=ir.Period.from_iso_string,
)

hist_db = ir.Databox()
hist_db["y"] = 100 * ir.log(fred_db["GDPC"])
hist_db["cpi"] = 100 * ir.log(fred_db["CPI"])
hist_db["ad_y"] = 4 * ir.diff(hist_db["y"])
hist_db["ad_cpi"] = 4 * ir.diff(hist_db["cpi"])

hist_db.to_csv(
    "data_files/hist_data.csv",
    date_formatter=ir.Period.to_iso_string,
)

start_filt = ir.qq(2015,1)
end_filt = ir.qq(2022,4)
filt_span = start_filt >> end_filt

filt_db = ir.Databox(
    obs_y=hist_db["y"](start_filt),
    obs_ad_y=hist_db["ad_y"](start_filt+1>>end_filt),
    obs_cpi=hist_db["cpi"](start_filt),
    obs_ad_cpi=hist_db["ad_cpi"](start_filt+1>>end_filt),

    std_shk_y_gap=ir.Series(periods=filt_span, values=0.5+np.random.uniform(size=len(filt_span)), ),
    std_shk_ad_cpi=ir.Series(periods=filt_span, values=1.5+np.random.uniform(size=len(filt_span)), ),
    shk_y_gap=ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), ),
    shk_ad_cpi=ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), ),
)

filt_db.clip(start_filt, end_filt, )
filt_db.apply(lambda x: x.round(6), )
filt_db.to_csv(
    "data_files/filt_data.csv",
    date_formatter=ir.Period.to_iso_string,
)


alt_filt_db = ir.Databox(
    obs_y=hist_db["y"],
    obs_cpi=hist_db["cpi"],

    std_shk_y_gap=ir.Series(periods=filt_span, values=0.5+np.random.uniform(size=len(filt_span)), ),
    std_shk_ad_cpi=ir.Series(periods=filt_span, values=1.5+np.random.uniform(size=len(filt_span)), ),
    shk_y_gap=ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), ),
    shk_ad_cpi=ir.Series(periods=filt_span, values=np.random.normal(size=len(filt_span)), ),
)

alt_filt_db.clip(start_filt, end_filt, )
alt_filt_db.apply(lambda x: x.round(6), )
alt_filt_db.to_csv(
    "data_files/alt_filt_data.csv",
    date_formatter=ir.Period.to_iso_string,
)


dates = {
    "start_filt": start_filt.to_iso_string(),
    "end_filt": end_filt.to_iso_string(), 
}

with open("data_files/dates.json", "wt+") as f:
    js.dump(dates, f, indent=4, )



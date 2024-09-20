

import irispie as ir

fred_db = ir.Databox.from_csv(
    "data_files/fred_data.csv",
    description_row=True,
    period_from_string=ir.Period.from_iso_string,
)

hist_db = ir.Databox()
hist_db["y"] = 100 * ir.log(fred_db["GDPC"])
hist_db["cpi"] = 100 * ir.log(fred_db["CPI"])
hist_db["ad_y"] = 4 * ir.diff(hist_db["y"])
hist_db["ad_cpi"] = 4 * ir.diff(hist_db["cpi"])
hist_db["rs"] = fred_db["TB3M"]

hist_db.to_csv("hist_data.csv", )


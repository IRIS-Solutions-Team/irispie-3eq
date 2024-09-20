
import irispie as ir

m = ir.Simultaneous.from_pickle_file("model.pkl", )

m.assign(
    std_shk_rs=3,
    std_shk_ad_cpi=1,
    std_shk_obs_cpi=1,
)
m.check_steady()
m.solve()

hist_db = ir.Databox.from_csv("hist_data.csv", )

obs_db = hist_db.copy(
    #source_names=("y", "ad_cpi", "rs", ),
    source_names=("y", "rs", "cpi", ),
    target_names=lambda n: f"obs_{n}",
)

start_filt = ir.qq(2010,1)
end_filt = ir.qq(2022,4)
filt_span = start_filt >> end_filt


multiplier_db = ir.Databox(
    std_shk_obs_cpi=ir.Series(periods=ir.qq(2022,1)>>ir.qq(2022,4), values=0, )
)

std_db = ir.Databox(
    std_shk_rs=10,
    std_shk_ad_y_tnd=ir.Series(periods=ir.qq(2019,3)>>ir.qq(2021,1), values=10, )
)

tv_stds = m.vary_stds(
    multiplier_db=multiplier_db,
    std_db=std_db,
    span=filt_span,
)

filt_db, info = m.kalman_filter(
    obs_db, filt_span,
    return_info=True,
    rescale_variance=True,
)

s = filt_db["smooth_med"]

tv_filt_db, tv_info = m.kalman_filter(
    obs_db | tv_stds, filt_span,
    return_info=True,
    rescale_variance=True,
    stds_from_data=True,
)
tv_s = tv_filt_db["smooth_med"]

std_scale = info["std_scale"]
m_rescaled = m.copy()
m_rescaled.rescale_stds(std_scale, )

_, info_rescaled = m_rescaled.kalman_filter(
    obs_db, filt_span,
    return_info=True,
    rescale_variance=True,
)


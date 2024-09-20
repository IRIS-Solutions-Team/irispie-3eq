#%% Create model object from source file

import irispie as ir
import json


def main() -> ir.Simultaneous:

    m = ir.Simultaneous.from_file(
        "closed_economy_qpm.model",
        linear=False,
    )

    ## Assign parameters

    parameters = ir.Databox(
        ss_rrs=0.5,
        ss_ad_cpi=2,
        ss_ad_y=1.5,
        c0_y_gap=0.75,
        c1_y_gap=0.10,
        c0_ad_cpi=0.55,
        c1_ad_cpi=0.10,
        c1_E_ad_cpi=1,
        c2_E_ad_cpi=0.1,
        c0_rs=0.75,
        c0_rrs_tnd=0.95,
        c1_mpr=4,
        c0_ad_y_tnd=0.95,

        std_shk_ad_y_tnd=3,
        std_shk_y_gap=1.0,
        std_shk_ad_cpi=2.0,
        std_shk_rs=0.3,
        std_shk_E_ad_cpi=0.1,
        std_shk_rrs_tnd=0.1,

        std_shk_obs_y=0.2,
        std_shk_obs_cpi=0.2,
    )
    parameters.set_description("Closed economy QPM model parameters", )

    print(parameters, )
    m.assign_strict(parameters, )
    ir.save_json(parameters, "parameters.json", )


    ## Calculate steady state

    m.steady()
    m.check_steady()
    print(m.get_steady_levels(round=4, ), )

    ## Calculate first-order solution matrices

    m.solve()

    m.to_json_file("model.json", indent=4, )
    m.to_pickle_file("model.pkl", )
    ir.save_pickle(m, "model_2.pkl", )

    return m


if __name__ == "__main__":
    m = main()


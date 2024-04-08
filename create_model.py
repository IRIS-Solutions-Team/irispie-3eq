## Create model object

import irispie as ir
import json


def main():

    m = ir.Simultaneous.from_file("linear_3eq.model", linear=True, )

    ## Assign parameters

    parameters = dict(
        ss_rrs = 0.5,
        ss_diff_cpi = 2,
        ss_diff_y_tnd = 1,
        c0_y_gap = 0.75,
        c1_y_gap = 0.10,
        c0_diff_cpi = 0.55,
        c1_diff_cpi = 0.10,
        c1_E_diff_cpi = 1,
        c0_rs = 0.75,
        c1_rs = 4,
        c0_y_tnd = 1,
        std_shk_y_tnd = 0.1,
        std_shk_y_gap = 1.0,
        std_shk_diff_cpi = 2.0,
        std_shk_rs = 0.3,
        std_shk_E_diff_cpi = 0.1,
    )

    m.assign(parameters, )

    with open("parameters.json", "wt+") as f:
        json.dump(m.get_parameters_stds(), f, indent=4, )

    ## Calculate steady state

    m.steady()
    chk = m.check_steady()

    print(m.get_steady_levels(round=4, ))

    ## Calculate first-order solution matrices

    m.solve(clip_small=False, )

    return m


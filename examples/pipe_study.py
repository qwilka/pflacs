"""Analysis of a pipe

https://www.engineeringtoolbox.com/barlow-d_1003.html
https://www.engineeringtoolbox.com/pe-pipe-dimensions-d_321.html
"""
import logging 

from pflacs import Premise, Calc
#import pdover2t


#logger = logging.getLogger(__name__)
logger = logging.getLogger()
logger.setLevel(logging.WARNING)  # logging.DEBUG 
lh = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# lh.setFormatter(formatter)
logger.addHandler(lh)

# https://stackoverflow.com/questions/49442523/prevent-showing-debugging-log-info-inside-ipython-shell
# logging.getLogger('parso.cache').disabled=True
# logging.getLogger('parso.cache.pickle').disabled=True
# logging.getLogger('parso.python.diff').disabled = True


def pipe_hoop_stress(P, D, t):
    """Calculate the hoop (circumferential) stress in a pipe 
    using Barlow's formula.

    Refs: https://en.wikipedia.org/wiki/Barlow%27s_formula
    https://en.wikipedia.org/wiki/Cylinder_stress

    :param P: the internal pressure in the pipe.
    :type P: float
    :param D: the outer diameter of the pipe.
    :type D: float
    :param t: the pipe wall thickness.
    :type t: float
    :returns: the hoop stress in the pipe.
    :rtype: float    
    """
    return P * D / 2 / t


def allowable_stress_unity_check(sigma, allowable, df=0.72):
    """Calculate the allowable stress unity check value.

    Refs: https://en.wikipedia.org/wiki/Permissible_stress_design
    https://en.wikipedia.org/wiki/Factor_of_safety

    :param sigma: applied stress level to be checked.
    :type sigma: float
    :param allowable: the allowable stress, e.g. the yield stress.
    :type allowable: float
    :param df: the design factor.
    :type df: float
    :returns: unity check value.
    :rtype: float    
    """
    return sigma / allowable * df


study_file = "pipe_study.vn3"  # .vn4 is sqlite

SETUP_NEW_STUDY = True
OPEN_EXISTING_STUDY = False

# SETUP_NEW_STUDY = False
# OPEN_EXISTING_STUDY = True

if SETUP_NEW_STUDY:
    print(f"Create a new study.")
    study_parameters = {
        "ys": 22.1 * 10**6,   # pipe yield strength in Pa
        "D": 110 * 10**-3,    # pipe outer diameter in m
        "P": 20 * 10**5,  # pipe internal pressure in Pa (20 bar)
        "t": 5 * 10**-3,
        "design_factor": 0.8,
    }

    basecase = Premise("Pipe study base case.",
                    parameters=study_parameters)
    basecase.plugin_func(pipe_hoop_stress)
    basecase.plugin_func(allowable_stress_unity_check)
    #basecase.plugin_func("pressure_containment_all", "pdover2t.dnvgl_st_f101")
    #basecase.plugin_func(pdover2t.dnvgl_st_f101.pressure_containment_all)
    lc1 = Premise("LoadCase1, pressure 15 bar.", basecase,
                    parameters={
                        "P": 15 * 10**5,  # pipe internal pressure in Pa
                    }    )
    lc1_pstress =  Calc("Calc pipe stress", lc1, 
                        funcname="pipe_hoop_stress",
                        )
    lc1_unity =  Calc("Stress unity check", lc1_pstress, 
                        funcname="allowable_stress_unity_check",
                        argmap={ "sigma":"_pipe_hoop_stress",
                                   "allowable":"ys",
                                   "df": "design_factor",
                        })
    # lc2 = Premise("LoadCase2, pressure 20 bar.", basecase)
    # lc3 = Premise("LoadCase3, pressure 25 bar.", basecase,
    #                 parameters={
    #                     "P": 25 * 10**5,  # pipe internal pressure in Pa
    #                 }    )
    lc2 = basecase.add_child(lc1.copy())
    lc2.name = "LoadCase2, pressure 20 bar."
    lc2.P = 20 * 10**5
    lc3 = basecase.add_child(lc1.copy())
    lc3.name = "LoadCase3, pressure 25 bar."
    lc3.P = 25 * 10**5

    for _n in basecase:
        if callable(_n):
            _n()

    basecase.savefile(study_file)


if OPEN_EXISTING_STUDY:
    print(f"Open Existing study from `pflacs` file «{study_file}».")
    #print("locals()", locals())
    basecase = Premise.openfile(study_file)



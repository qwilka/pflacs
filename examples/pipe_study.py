"""Analysis of a pipe

https://www.engineeringtoolbox.com/barlow-d_1003.html
https://www.engineeringtoolbox.com/pe-pipe-dimensions-d_321.html
"""

from pflacs import Premise, Calc
import pdover2t


def pipe_hoop_stress(P, D, t):
    """Calculate the hoop (circumferential) stress in a pipe 
    using Barlow's formula.

    Ref: https://en.wikipedia.org/wiki/Barlow%27s_formula
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


study_file = "pipe_study.pflacs"

SETUP_NEW_STUDY = False
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
    }

    basecase = Premise("Pipe study base case.",
                    parameters=study_parameters,
                    vnpkl_fpath=study_file )
    basecase.plugin_func(pipe_hoop_stress)
#basecase.plugin_func("pressure_containment_all", "pdover2t.dnvgl_st_f101")
    basecase.plugin_func(pdover2t.dnvgl_st_f101.pressure_containment_all)
    # lc1 = Premise("Load case 1, pressure 20 bar.",
    #                 parameters={
    #                     "P": 20 * 10**5,  # pipe internal pressure in Pa
    #                 }    )
    basecase.savefile()


if OPEN_EXISTING_STUDY:
    print(f"Open Existing study from `pflacs` file «{study_file}».")
    #print("locals()", locals())
    basecase = Premise.openfile(study_file)



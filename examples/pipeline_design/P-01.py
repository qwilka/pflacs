"""Analysis of gas pipeline «P-01»
"""
import logging

import numpy as np

import pdover2t
from pdover2t.dnvgl_st_f101 import factor
from pflacs import Premise, Calc

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # logging.DEBUG 
lh = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# lh.setFormatter(formatter)
logger.addHandler(lh)


field_params = {
    "ast_country": "IRL",
    "ast_desc": "Pflacs oil&gas field, subsea",
    "ast_domain": "SUBSEA",
    "ast_field": "Pflacs",
    "ast_url": "IRL:PFLACS:SUBSEA",
    "design_life": 25,
}
constants = {
    "g": 9.81, 
}

pipeline_params = {
    "ast_desc": "P-01 gas pipeline",
    "ast_tag": "P-01",
    "ast_uri": "IRL:PFLACS:P-01",
    "h_l": [-250., -440.],
    "material": "CMn",
    "E": 207.e9,
    "nu": 0.3,
    "SMYS": 450.e6,
    "SMTS": 535.e6,
    "t_corr": 0.0005,
    "t_fab": 0.001,
}
process_params = {
    "h_ref": 30.,
    "p_d": 240e5,
    "rho_cont": 275.,
    "rho_t": 1027.,
    "T": 60,
}
design_params = {
    "alpha_spt": factor.alpha_spt_map("high"),
    "alpha_fab": factor.alpha_fab_map("UOE"),
    "alpha_U": factor.alpha_U_map(1.0),   
    "gamma_inc": 1.1,
    "gamma_m": factor.gamma_m_map("ULS"),
}
env_params = {
    "rho_water": 1027.,    
}

vnpkl_file = "IRL--PFLACS--P-01.vnpkl"


rootnode = Premise("Pflacs oil&gas field, subsea", 
                parameters={ 
                    **field_params, 
                    **constants,
                    **env_params,
                },
                data={"desc": "Top-level field details, environmental and universal parameters."},
                vnpkl_fpath=vnpkl_file)

rootnode.plugin_func("pressure_containment_all", "pdover2t.dnvgl_st_f101")
rootnode.plugin_func("pipe_collapse_all", "pdover2t.dnvgl_st_f101")


P01 = Premise("P-01 gas pipeline", 
                parent=rootnode,
                parameters={
                    **pipeline_params,
                    **process_params,
                    **design_params,
                },
                data={"desc": "P-01 gas pipeline."})

P01_1 = Premise("P-01 section 1, KP 0-0.3", 
                parent=P01,
                parameters={
                    "alpha_mpt": factor.alpha_mpt_map("high"),
                    "alpha_spt": factor.alpha_spt_map("high"),
                    "gamma_SCLB": factor.gamma_SCLB_map("high"),
                    "gamma_SCPC": factor.gamma_SCPC_map("high"),
                    "h_l": -370,
                    "LC": 2,
                    "SC": "high",
                    "D": 0.6172 + 2*0.0242,
                    "t": 0.0242,
                    "KP_range": [0, 0.3],
                })

pcont1 = Calc("pressure containment (operation)", parent=P01_1,
                data={"desc": "Pressure contain calcs."},
                funcname="pressure_containment_all") 
# pcont_test1 = Calc("pressure containment (system test)", parent=pcont1,
#                 data={"desc": "Pressure contain calcs."},
#                 funcname="pressure_containment_all") 

pcoll1 = Calc("pipe collapse", parent=P01_1,
                data={"desc": "Pipe collapse calcs."},
                funcname="pipe_collapse_all") 


P01_2 = P01.add_child( P01_1.copy() )
P01_2.name = "P-01 section 2, KP 0.3-15"
P01_2.KP_range = [0.3, 15.0]
P01_2.h_l = -340
P01_2.LC = 1
P01_2.SC = "medium"
P01_2.alpha_mpt = factor.alpha_mpt_map("medium")
P01_2.alpha_spt = factor.alpha_spt_map("medium")
P01_2.gamma_SCLB = factor.gamma_SCLB_map("medium")
P01_2.gamma_SCPC = factor.gamma_SCPC_map("medium")
P01_2.D = 0.6172 + 2*0.0242
P01_2.t = 0.0242

pcont2 = P01_2.get_child_by_name("pressure containment")
pcoll2 = P01_2.get_child_by_name("pipe collapse")

P01_3 = P01.add_child( P01_2.copy() )
P01_3.name = "P-01 section 3, KP 15-79.7"
P01_3.KP_range = [15.0, 79.7]
P01_3.h_l = -250
P01_3.D = 0.6172 + 2*0.0214
P01_3.t = 0.0214

pcont3 = P01_3.get_child_by_name("pressure containment")
pcoll3 = P01_3.get_child_by_name("pipe collapse")

# P01_2 = Premise("P-01 section 2, KP 0.3-15", 
#                 parent=P01,
#                 parameters={
#                     "KP": [0.3, 15.0],
#                     "h_l": -420,
#                     "LC": 1,
#                     "D": 0.6172 + 2*0.0242,
#                     "t": 0.0242,
#                 },
#                 data={"desc": "P-01 section 2, KP 0.3-15."})

# P01_3 = Premise("P-01 section 3, KP 15-79.7", 
#                 parent=P01,
#                 parameters={
#                     "KP": [15.0, 79.7],
#                     "LC": 1,
#                     "D": 0.6172 + 2*0.0214,
#                     "t": 0.0214,
#                 },
#                 data={"desc": "P-01 section 3, KP 15-79.7."})





rootnode.savefile()
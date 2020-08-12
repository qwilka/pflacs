"""Pflacs analyses of Åsgard flowlines.

Setting up Åsgard field-level parameters.

References
==========
Chapter 23 in [@bai2014subsea] 
https://factpages.npd.no/en/field/pageview/all/43765


https://qwilka.github.io/gis/1/#10/65.0655/6.7834/g2-nof-noi-nop
https://factmaps.npd.no/factmaps/3_0/?run=FieldByNPDID&NPDID=43765
"""
import logging

import numpy as np

import pdover2t
from pflacs import Premise, Calc

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # logging.DEBUG 
lh = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# lh.setFormatter(formatter)
logger.addHandler(lh)


field_params = {
    "ast_country": "NOR",
    "ast_desc": "Åsgard oil&gas field, subsea",
    "ast_domain": "subsea",
    "ast_field": "Åsgard",
    "ast_operator": "Equinor",
    "ast_url": "NOR:ÅSGARD:SUBSEA",
    "ast_links": [
        {"url": "https://factpages.npd.no/en/field/pageview/all/43765", "type":"info"},
        {"url": "https://factmaps.npd.no/factmaps/3_0/?run=FieldByNPDID&NPDID=43765", "type":"gis"},
        {"url": "https://qwilka.github.io/gis/1/#10/65.0655/6.7834/g2-nof-noi-nop", "type":"gis"}
    ],
    "design_life": None,
}

constants = {
    "g": 9.81, 
}

P101 = {
    "ast_desc": "P101 gas pipeline",
    "ast_tag": "P101",
    "ast_uri": "NOR:ÅSGARD:P101",

    "pipe_rho": 7850.0,
    "pipe_Do": 258.8e-3,
    "pipe_wt": 11.6e-3,

    "p_d": 370e5,
    "p_mop": 330e5,
    "coat_wt": 53e-3,
    "coat_rho": 1190.0,
    "WD_range": [306.0, 322.0],

    "pl_sub_wgt": 46.4,  # pipeline submerged weight per unit length
    "rlt": 121.e3        # residual lay tension
    ""
}

process_params = {
    "h_ref": 30.,
    "p_d": 240e5,
    "rho_cont": 275.,
    "rho_t": 1027.,
    "T": 60,
}
design_params = {
    "h_l": [-250., -440.],
    "material": "CMn",
    "E": 207.0*10**9,
    "nu": 0.3,
    "SMYS": 450.e6,
    "SMTS": 535.e6,
    "t_corr": 0.0005,
    "t_fab": 0.001,
    'alpha_fab': 1.00,
    'alpha_mpt': 1.088,
    'alpha_spt': 1.05,
    "alpha_U": 1.0,  
    "gamma_inc": 1.1,
    'gamma_m': 1.15,
    'gamma_SCLB': 1.14,
    'gamma_SCPC': 1.138,
    "SC": "medium",
}
env_params = {
    "rho_water": 1027.,    
}


vnpkl_file = "/home/develop/engineering/src/scratch/pflacs_test/IRL--PFLACS--P-01.vnpkl"


rootnode = Premise("Pflacs oil&gas field, subsea", 
                parameters={ 
                    **field_params, 
                    **constants,
                    **env_params,
                },
                data={"desc": "Top-level field details, environmental and universal parameters."},
                vnpkl_fpath=vnpkl_file)
P01 = Premise("P-01 gas pipeline", 
                parent=rootnode,
                parameters={
                    **pipeline_params,
                    **process_params,
                    **design_params,
                },
                data={"desc": "P-01 gas pipeline."})

P01_1 = Premise("P-01 pipeline section 1, KP 0-0.3", 
                parent=P01,
                parameters={
                    "KP": [0, 0.3],
                    "h_l": -370,
                    "LC": 2,
                    "SC": "high",
                    "D": 0.6172 + 2*0.0242,
                    "t": 0.0242,
                },
                data={"desc": "P-01 section 1, KP 0-0.3."})

rootnode.plugin_func("pipe_physical_props", "pdover2t", argmap={
    "Do": "D",
    "WT": "t",
})
rootnode.plugin_func("pressure_containment_all", "pdover2t.dnvgl_st_f101")
rootnode.plugin_func("pipe_collapse_all", "pdover2t.dnvgl_st_f101")

lc1_pprops = Calc("Calc: pipe properties", parent=P01_1, 
                data={"desc": "pipe physical properties."},
                funcname="pipe_physical_props") 

lc1_cont = Calc("Calc: pressure containment", parent=P01_1, 
                parameters={
                    "h_l": -370,
                },
                data={"desc": "pressure containment calcs."},
                funcname="pressure_containment_all") 


lc1_collapse = Calc("Calc: pipe collapse", parent=P01_1, 
                parameters={
                    "h_l": -370,
                },
                data={"desc": "pipe collapse calcs."},
                funcname="pipe_collapse_all") 


rootnode.plugin_func("vertical_stability", "pdover2t.dnvgl_st_f101")
rootnode.plugin_func("lateral_stability", "pdover2t.dnvgl_st_f101")

lc1_vstab = Calc("Calc: vertical stability", parent=P01_1, 
                data={"desc": "pipeline vertical stability check."},
                funcname="vertical_stability") 

lc1_lstab = Calc("Calc: lateral stability", parent=P01_1, 
                data={"desc": "pipeline lateral stability check."},
                funcname="lateral_stability") 

P01_2 = P01.add_child(P01_1.copy())
P01_2.name = "P-01 pipeline section 2, KP 0.3-15"
P01_2.KP = [0.3, 15.0]
P01_2.h_l = -420
P01_2.LC= 1
P01_2.D = 0.6172 + 2*0.0242
P01_2.t = 0.0242

P01_3 = P01.add_child(P01_2.copy())
P01_3.name = "P-01 pipeline section 3, KP 15-79.7"
P01_3.KP = [15.0, 79.7]
#P01_3.h_l = -420
#P01_3.LC= 1
P01_3.D = 0.6172 + 2*0.0214
P01_3.t = 0.0214


P07 = rootnode.add_child(P01.copy())
P07.name = "P-07 oil pipeline"
P07_1 = P07.get_child_by_name("P-01 pipeline section 1, KP 0-0.3")
P07_1.name = "P-07 pipeline section 1, KP 0-1.5"
P07_2 = P07.get_child_by_name("P-01 pipeline section 2, KP 0.3-15")
P07_2.name = "P-07 pipeline section 2, KP 1.5-6.9"
P07_3 = P07.remove_child(2)
del(P07_3)

for _n in rootnode:
    if callable(_n):
        _n()

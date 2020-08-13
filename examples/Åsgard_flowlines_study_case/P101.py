"""

References
«Subsea pipeline design, analysis, and installation» Bai & Bai, 2014 ed, Chapter 23
"""

from pflacs import Premise, Calc, Table
import pdover2t


# Uncomment the following line to enable extended log messages.
#pdover2t.utilities.turn_on_logging(level="WARNING", timestamp=False) 

P101_data = {
    "Do": 258.5e-3,   # pipe outer diameter (m)
    "WT": 15.6e-3,   # pipe wall thickness (m)
    "pipe_ρ": 7850.0,     # pipe steel density (kg/m3)
    "coat": [(53.e-3, 1190.0)], # [(thickness, density)]
    "joint_length": 12.2,    
    "seawater_ρ": 1027.0,     # seawater density (kg/m3)
}

# name, params, 
pipemass_branch = [
    {"name":"calc Di", "funcname":"calc_pipe_Di"},
    {"name":"calc CSA", "funcname":"pipe_CSA"},
]




def make_calc_branch(ndata):
    _parent = None
    for _d in ndata:
        _name = _d.get("name")
        _paras = _d.get("parameters", None)
        _funcname = _d.get("funcname", None)
        _argmap = _d.get("argmap", None)
        _n = Calc(_name, _parent, parameters=_paras, funcname=_funcname,
            argmap=_argmap)
        _parent = _n
    return _n._root

calctree = make_calc_branch(pipemass_branch)

P101 = Premise("P101", 
                parameters=P101_data,
                data={"desc": "Top-level field details, environmental and universal parameters."})


P101.plugin_func("calc_pipe_Di", "pdover2t.pipe")
P101.plugin_func("pipe_CSA", "pdover2t.pipe")

P101_z1 = Premise("P101 zone1", parent=P101)
P101_z2 = Premise("P101 zone2", parent=P101)

#P101.plugin_func("calc_pipe_Di", "pdover2t.pipe")

calc_joint_mass = Calc("calc Di", parent=P101_z1, 
                funcname="calc_pipe_Di")




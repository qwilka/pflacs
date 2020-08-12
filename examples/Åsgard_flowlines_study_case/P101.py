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




P101 = Premise("P101", 
                parameters=P101_data,
                data={"desc": "Top-level field details, environmental and universal parameters."})

P101_z1 = Premise("P101 zone1", parent=P101)
P101_z2 = Premise("P101 zone2", parent=P101)

P101.plugin_func("calc_pipe_Di", "pdover2t.pipe")

calc_joint_mass = Calc("calc Di", parent=P101_z1, 
                funcname="calc_pipe_Di")


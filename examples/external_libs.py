"""
https://github.com/bjornaa/seawater
https://github.com/benranderson/wall
"""

from pflacs import Premise
import numpy
import wall
import seawater

base = Premise("Basecase")
base.add_param("water_depth", 110, "water depth (m)")
base.add_param("rho_seawater", 1025, "assumed water density (kg/m3)")   
base.add_param("pressure", desc="pressure (Pa)")

base.plugin_func(wall.pressure_head, argmap={"h":"water_depth", "rho":"rho_seawater"})
base.pressure = base.pressure_head()
print(f'{base.name} pressure = {base.pressure}') 

base.add_param("lat", 53.2, "geographical latitude")
base.add_param("S", 35, "water salinity")
base.add_param("T", 8, "water temperature (°C)")

base.plugin_func(seawater.dens)
base.add_param("rho_seawater_check", desc="calculated water density (kg/m3)")
base.rho_seawater_check = base.dens()
print(f'{base.get_param_desc("rho_seawater_check")} = {base.rho_seawater_check}')
if base.rho_seawater != base.rho_seawater_check:
    print(f"Warning: calculated seawater density {base.rho_seawater_check} not equal to assumed value {base.rho_seawater}.")

base.plugin_func(numpy.interp, 
            argmap={"x":"S", "xp":"salinities", "fp":"densities"}, 
            newname="interp_water_density")

base.add_param("salinities", desc="water salinity range")
base.add_param("densities", desc="water density range")
base.salinities = numpy.linspace(30, 40, 11)
base.densities = base.dens(S=base.salinities)

rho_interp = base.interp_water_density()
print(f"Interpolated water density = {rho_interp}, for salinity = {base.S} ")

rho_interp = base.interp_water_density(S=39.5)
print(f"Interpolated water density = {rho_interp}, for salinity = 39.5 ")

base.savefile("external_libs_test.pflacs")


from pflacs import Premise
import numpy
from wall import pressure_head
from seawater import dens


study_file = "external_libs_test.pflacs"

print(f"Open Existing study from `pflacs` file «{study_file}».")
#print("locals()", locals())
base = Premise.openfile(study_file)

print(f'{base.name} pressure = {base.pressure}') 

print(f'{base.get_param_desc("rho_seawater_check")} = {base.rho_seawater_check}')
if base.rho_seawater != base.rho_seawater_check:
    print(f"Warning: calculated seawater density {base.rho_seawater_check} not equal to assumed value {base.rho_seawater}.")


rho_interp = base.interp_water_density()
print(f"Interpolated water density = {rho_interp}, for salinity = {base.S} ")

rho_interp = base.interp_water_density(S=39.5)
print(f"Interpolated water density = {rho_interp}, for salinity = 39.5 ")

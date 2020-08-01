"""Analysis of a pipe

https://www.engineeringtoolbox.com/barlow-d_1003.html
https://www.engineeringtoolbox.com/pe-pipe-dimensions-d_321.html
"""

from pflacs import Premise, Calc

from pipe_study import pipe_hoop_stress


study_file = "pipe_study.vn3"

print(f"Open Existing study from `pflacs` file «{study_file}».")
#print("locals()", locals())
basecase = Premise.openfile(study_file)



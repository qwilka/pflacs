import logging 

from pflacs import Premise, Calc


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # logging.DEBUG 
lh = logging.StreamHandler()
logger.addHandler(lh)

pflacs_filepath = "very_simple_study.pflacs"

print(f"Open existing study from `pflacs` file «{pflacs_filepath}».")
basecase = Premise.openfile(pflacs_filepath)
print(basecase.to_texttree())

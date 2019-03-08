import logging 

from pflacs import Premise, Calc


logger = logging.getLogger()
logger.setLevel(logging.INFO)  # logging.DEBUG 
lh = logging.StreamHandler()
logger.addHandler(lh)

vnpkl_file = "IRL--PFLACS--P-01.pflacs"


rootnode = Premise.openfile(vnpkl_file)
print(rootnode.to_texttree())

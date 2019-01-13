from pflacs import Premise, Parameter

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # logging.DEBUG 
lh = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# lh.setFormatter(formatter)
logger.addHandler(lh)

# https://github.com/ipython/ipython/issues/10946
# https://stackoverflow.com/questions/49442523/prevent-showing-debugging-log-info-inside-ipython-shell
# logging.getLogger('parso.cache').disabled=True
# logging.getLogger('parso.cache.pickle').disabled=True
# logging.getLogger('parso.python.diff').disabled = True

def pf(age, date, name="NO NAME", address=None):    
    """pf function this is doc string"""                 
    print("this is pf function name {}, age {}, date {}, address {}".format(name,age, date, address))



rootnode = Premise("root LC")
rootnode.import_params_pyfile("pars.py")
rootnode.plugin_func(pf)

rootnode.add_param("date", 1988)
rootnode.pf(88, name=22) 
rootnode.add_param("age", 100)
rootnode.pf()

c1 = Premise("1st child LC", rootnode)
c1.pf(age=250)
c1.pf()

import math

def math_sqrt(x):                                       
   return math.sqrt(x)

rootnode.plugin_func(math_sqrt, argmap={"x": "xxx"})
c1.math_sqrt(xxx=4)
c1.add_param("xxx", 77)
c1.math_sqrt()

c2 = Premise("2nd child LC", rootnode, parameters={"age":998}, data={"testing":{"value":12345}})

c3 = Premise("3rd child LC", rootnode, data={"params":{"age":{"value":7654}}, "dummy":{"value":4321}})

g1 = Premise("1st grandchild", c2)
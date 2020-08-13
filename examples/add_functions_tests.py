import logging

from pflacs import Premise, Calc, Table

import numpy as np

logger = logging.getLogger()
logger.setLevel(logging.WARNING)  # logging.DEBUG  logging.WARNING
lh = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
lh.setFormatter(formatter)
logger.addHandler(lh)

def addAB(a,b) -> "AplusB":
    return a+b

def addCD(c,d):
    return c+d


params1 = {
    "a": 2.2,
    "b": 10,
}
params2 = {
    #"c": 100,    
    "c": np.array([10,20,30,1001.]),
    "d": 100.,
}

rootnode = Premise("Root Node", 
                parameters={ 
                    **params1, 
                },
                data={"desc": "Top-level parameters."},
                vnpkl_fpath="add_tests.vn3")

base1 = Premise("Base 1", parent=rootnode) 

rootnode.plugin_func(addAB)
rootnode.plugin_func(addCD, argmap={"return":"CplusD"})

if False:
    addab = Calc("Calc: addAB", parent=rootnode, 
                    data={"desc": "First calc."},
                    funcname="addAB") 

    addcd = Calc("Calc: addCD", parent=addab, 
                    parameters={ 
                        **params2, 
                    },
                    data={"desc": "2nd calc."},
                    funcname="addCD") 

    total = Calc("Calc: add results", parent=addcd, 
                    data={"desc": "add results"},
                    funcname="addAB", argmap={"a":"AplusB", "b":"CplusD", "return":"TOTAL"}) 
    base1.add_param("TOTAL", linkid=total._nodeid)
    base1.add_param("CplusD", linkid=addcd._nodeid)

    table = Table("add results", parent=total, paranames=["a","b", "c", "d", "TOTAL"])
    table2 = Table("test table", parent=base1, paranames=["a","CplusD", "TOTAL"])

    # for _n in rootnode:
    #     if callable(_n):
    #         _n()

    # for _n in rootnode:
    #     if type(_n) is Calc:
    #         _n()

    # for _n in rootnode:
    #     if type(_n) is Table:
    #         _n()

if True:
    a_kwargs = {"a":-10000}
    add_branch = [
        {"name":"a + b", "funcname":"addAB", "kwargs":a_kwargs},
        {"name":"c + d", "funcname":"addCD", "parameters":params2},
        {"name":"total", "funcname":"addAB", "argmap":{"a":"AplusB", "b":"CplusD", "return":"TOTAL"}}
    ]




    def make_calc_branch(ndata):
        _parent = None
        for _d in ndata:
            _name = _d.get("name")
            _paras = _d.get("parameters", None)
            _funcname = _d.get("funcname", None)
            _argmap = _d.get("argmap", None)
            _kwargs = _d.get("kwargs", None)
            _n = Calc(_name, _parent, parameters=_paras, funcname=_funcname,
                argmap=_argmap, kwargs=_kwargs)
            _parent = _n
        return _n._root

    calctree = make_calc_branch(add_branch)
    rootnode.add_child(calctree)
    rootnode.update()
    ab = rootnode.find_one_node("name", value="a + b")
    cd = rootnode.find_one_node("name", value="c + d")
    total = rootnode.find_one_node("name", value="total")

#rootnode.update()

#rootnode.savefile("ADD.vn3")

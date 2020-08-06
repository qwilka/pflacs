from pflacs import Premise, Calc, Table

import numpy as np

def addAB(a,b) -> "AplusB":
    return a+b

def addCD(c,d):
    return c+d


params = {
    "a": 2.2,
    "b": 10,
    "c": 100,    
    "d": 100.,
}

rootnode = Premise("Root Node", 
                parameters={ 
                    **params, 
                },
                data={"desc": "Top-level parameters."},
                vnpkl_fpath="add_tests.vn3")

rootnode.plugin_func(addAB)
rootnode.plugin_func(addCD, argmap={"return":"CplusD"})
rootnode.add_param("TOTAL")

addab = Calc("Calc: addAB", parent=rootnode, 
                data={"desc": "First calc."},
                funcname="addAB") 

addcd = Calc("Calc: addCD", parent=addab, 
                parameters={"c":np.array([10,20,30,1001.])},
                data={"desc": "2nd calc."},
                funcname="addCD") 

total = Calc("Calc: add results", parent=addcd, 
                data={"desc": "add results"},
                funcname="addAB", argmap={"a":"AplusB", "b":"CplusD", "return":"TOTAL"}) 

table = Table("results table", parent=total, paranames=["a","b", "c", "d", "TOTAL"])

for _n in rootnode:
    if callable(_n):
        _n()
                
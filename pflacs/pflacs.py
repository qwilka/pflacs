"""
Copyright © 2018 Stephen McEntee
Licensed under the MIT license. 
See «pflacs» LICENSE file for details:
https://github.com/qwilka/pflacs/blob/master/LICENSE
"""
import ast
import collections
import functools
import importlib
import inspect
import copy
#import os
#import string
import pathlib
import re
import logging
import sys
#import time
#from traceback import extract_stack
import types
import warnings
logger = logging.getLogger(__name__)

from vntree import Node, NodeAttr, TreeAttr


logger.debug("#### in pflacs.py: DEBUG this is a test  ####")

import numpy as np

import pandas as pd
from tables import NaturalNameWarning
warnings.simplefilter('ignore', NaturalNameWarning)  


class Parameter:
    """NOTE this class is not related to Python's inspect.Parameter """
    def __init__(self, name, desc=""):
        self.name = name
        self.desc = desc
        self.access_coord = None
    def __get__(self, instance, owner):
        if instance:
            _val = instance.data["params"].get(self.name, None)
            # if self.access_coord is None:
            #     self.access_coord = instance._coord
            if _val and isinstance(_val, dict) and "value" in _val:
                _val = _val["value"] 
                # print("Parameter in node: ", instance._coord, "accessed from: ", self.access_coord)
                # self.access_coord = None
            if _val is None and instance.parent:
                _val = getattr(instance.parent, self.name)
        elif owner:
            _val = None 
        return _val
    def __set__(self, instance, value):
        if self.name not in instance.data["params"]:
            instance.data["params"][self.name] = {}
            instance.data["params"][self.name]["desc"] = self.desc
        instance.data["params"][self.name]["value"] = value
    def __delete__(self, instance):
        del instance.data["params"][self.name]
    def __set_name__(self, owner, name):  # not required: this is only called for attributes defined when the class is created
        self.name = name
        #print("Parameter __set_name__ call: ", self.name)
    



class Function:
    def __init__(self, func, argmap=None):
        self.name = func.__name__
        self._sig = inspect.signature(func)
        self._func = func
        # if not isinstance(argmap, (dict, None)):
        #     raise TypeError('Function: argument «argmap» not correctly specified.')
        if isinstance(argmap, dict):
            self._argmap = argmap
        else:
            self._argmap = {}
        self._instance = None
        #self._owner = None
    def __get__(self, instance, owner):
        logger.debug("Function.__get__ «instance» {}, «owner» {}".format(instance, owner))
        self._instance = instance
        #self._owner = owner
        return self
    def __call__(self, *args, **kwargs):
        #_xkwargs = {}
        logger.debug("Function.__call__: function «%s».«%s»; args «%s»; kwargs «%s»" % (self._instance, self.name, args, kwargs))
        _xkwargs = copy.deepcopy(kwargs)
        for ii, (_key, _para) in enumerate(self._sig.parameters.items()):
            logger.debug("Function.__call__: function «%s».«%s»; parameter name «%s»" % (self._instance, self.name, _para.name))
            if ii<len(args):
                continue
            if _para.name in self._argmap and self._argmap[_para.name] in kwargs:
                _parval = _xkwargs.pop(self._argmap[_para.name])
                _xkwargs[_para.name] = _parval
            elif _para.name in kwargs:
                logger.debug("Function.__call__: WARNING «%s».«%s»; parameter name «%s» is keyword argument in original function «%s» (binding nonetheless)." % (self._instance, self.name, _para.name, self._func.__name__))
                continue
            if self._argmap and _para.name in self._argmap.keys():
                _inst_param = self._argmap[_para.name]
            else:
                _inst_param = _para.name
            # if _inst_param in self._instance.params:
            #     _xkwargs[_para.name] = self._instance.params[_inst_param]
            if self._instance.is_param(_inst_param):
                #_xkwargs[_para.name] = self._instance.get_param(_inst_param)
                #_xkwargs[_para.name] = self._instance.params.get(_inst_param)
                _xkwargs[_para.name] = getattr(self._instance, _inst_param)
        logger.debug("Function.__call__: function «%s».«%s»; bind args: %s & kwargs: %s;" % (self._instance, self.name, args, _xkwargs))
        try:
            #_bound = self._sig.bind(*args, **kwargs, **_xkwargs)
            _bound = self._sig.bind(*args, **_xkwargs)
        except TypeError as err:
            _argname = ""
            _mat = re.search(r"\'(\w+)\'\s*$", str(err))
            if _mat:
                _argname = _mat.groups()[0]
                if _argname in self._argmap:
                    _argname = self._argmap.get(_argname)
                    _argname = "missing parameter «{}»".format(_argname)
            logger.error("Function.__call__: function «%s».«%s»; %s; (original function error: %s)" % (self._instance, self.name, _argname, err))
            return False
        #print(self._instance, _bound)
        #self._instance._boundargs = _bound
        self._instance._arguments = copy.deepcopy(_bound.arguments)
        #return self._func(*_bound.args, **_bound.kwargs)
        _result = self._func(*_bound.args, **_bound.kwargs)
        if self._instance and getattr(self._instance, "_result_attr", None):
            _internals = []
            _argmap_ret = self._argmap.get("return", None)
            if _argmap_ret is None or (isinstance(_argmap_ret, str) and _argmap_ret.strip()==""):
                _attr_name = "_"+self.name
                self._instance.add_param(_attr_name, value=_result, desc="«internal»")
                _internals.append(_attr_name)
            elif isinstance(_argmap_ret, str):
                _argmap_ret = _argmap_ret.strip()
                try:
                    _eval_ret = ast.literal_eval(_argmap_ret)
                except ValueError:
                    _eval_ret = _argmap_ret
                if isinstance(_eval_ret, str):
                    _attr_name = _eval_ret
                    self._instance.add_param(_eval_ret, value=_result, desc="«internal»")
                    _internals.append(_attr_name)
                elif isinstance(_eval_ret, dict) and isinstance(_result, dict):
                    for k, v in _result.items():
                        if k in _eval_ret:
                            _attr_name = _eval_ret[k]
                        else:
                            _attr_name = k
                        self._instance.add_param(_attr_name, value=v, desc="«internal»")
                        _internals.append(_attr_name)
            self._instance._internals = _internals
            #self._instance._externals = list(self._sig.parameters.keys())
        return _result



class Loadcase(Node):
    """Class for creating pflacs nodes.

    :param name: node name
    :type name: str or None
    :param parent: The parent node of this node.
    :type parent: Node or None
    :param data: Dictionary containing node data.
    :type data: dict or None
    :param treedict: Dictionary specifying a complete tree.
    :type treedict: dict or None
    """
    _clsname = NodeAttr()
    _result_attr = NodeAttr()
    desc = NodeAttr()
    #_hdf_fpath = TreeAttr("_vntree_meta")

    def __init__(self, name=None, parent=None, parameters=None, pyfile=None,
                data=None, treedict=None, vnpkl_fpath=None):
        super().__init__(name, parent, data, treedict, vnpkl_fpath)
        #self.set_data("params", value={})
        params = {}
        if parameters and isinstance(parameters, dict):
            for _k, _v in parameters.items():
                if isinstance(_v, dict) and "value" in _v:
                    params[_k] = _v
                else:
                    params[_k] = {"value": _v}
        if "params" in self.data and isinstance(self.data["params"], dict):
            _pars = copy.deepcopy(self.data["params"])
            if params and isinstance(params, dict):
                _pars.update(copy.deepcopy(params))
            params = _pars
        self.data["params"] =  {}
        if params and isinstance(params, dict):
            self.import_params(params)
        if "plugins" in self.data:
            _plist = copy.copy(self.data["plugins"])
        else:
            _plist = None
        self.data["plugins"] =  []
        if _plist:
            for _plug in _plist:
                self.plugin_func(*_plug)
        # if pyfile:
        #     self.import_params_pyfile(pyfile)
        self._clsname = self.__class__.__name__
        self._result_attr = False
        # if hdf_fpath and isinstance(hdf_fpath, str):
        #     self._hdf_fpath = hdf_fpath


    @property
    def _hdf_fpath(self):
        """Attribute that indicates the path for the HDF5 file.
        """
        if self._vnpkl_fpath:
            _pp = pathlib.Path(self._vnpkl_fpath)
            return str(_pp.with_suffix(".hdf5"))
        else:
            return None


    def add_param(self, name, value=None, desc="«add_param»", **kwargs):
        if name in self.data["params"]:
            logger.debug("add_param: {} is already param of «{}»!".format(name, self.name))
        else:
            setattr(self.__class__, name, Parameter(name, desc))
            setattr(self, name, value)
        return True


    def is_param(self, name):
        _exists = False
        if name in self.data["params"]:
            _exists = True
        elif self.parent:
            _exists = self.parent.is_param(name)
        return _exists


    def import_params(self, params):
        for _key, _pdict in params.items():
            # if callable(_val) or isinstance(_val, ModuleType):
            #     continue
            self.add_param(name=_key, **_pdict)
        return True

    # def import_params_pyfile(self, pyfile):
    #     gbl_var={}; loc_var={}
    #     try:
    #         exec(compile(open(pyfile).read(), pyfile, 'exec'), gbl_var, loc_var)
    #     except Exception as err:
    #         logger.error("%s.import_params_pyfile: cannot import parameters from file %s; %s" % (self.__class__.__name__, pyfile, err))
    #         return False
    #     #return self.import_params(loc_var)
    #     for _key, _val in loc_var.items():
    #         if callable(_val) or isinstance(_val, types.ModuleType):
    #             continue
    #         self.add_param(_key, _val)
    #     return True



    def plugin_func(self, func, module=None, argmap=None, newname=None):
        """Patch a function into «Loadcase» class as an instance bound method.
        """
        logger.info("%s.plugin_func: patching function «%s»." % (self.__class__.__name__, func))
        # test if «function» is valid for Pflacs:
        err = "arg «func» must be str or function; «module» must be str."
        if isinstance(func, str):
            if module and isinstance(module, str):
                _mod = importlib.import_module(module)
                _function = getattr(_mod, func)
            else:
                _function = locals().get(func)
        elif isinstance(func, types.FunctionType):
            _function = func
        else:
            _function = None
            #err = "arg «func» type must be str or function."
        if _function is None:
            logger.error("%s.plugin_func: args «func»=«%s» «module»=«%s» not valid: %s" % (self.__class__.__name__, func,module, err))
            return False
        _argmp = {}
        if _function.__annotations__:
            _argmp = copy.copy(_function.__annotations__)
        if argmap and isinstance(argmap, dict):
            _argmp.update(argmap)
        try:
            _sig = inspect.signature(_function)
        except (ValueError, TypeError) as err:
            logger.error("%s.plugin_func: function «%s» is not valid for Pflacs: %s" % (self.__class__.__name__, _function.__name__, err))
            return False
        if newname:
            _methodname = newname
        else:
            _methodname = _function.__name__
        setattr(self.__class__, _methodname, Function(_function, argmap=_argmp))
        functools.update_wrapper(getattr(self.__class__, _methodname), _function)
        self.data["plugins"].append( (_function.__name__, module, _argmp, newname) )
        return True


    def from_treedict(self, treedict):
        if "data" in treedict:
            self.data = collections.defaultdict(dict, treedict["data"])
        for key, val in treedict.items():
            if key in ["parent", "childs", "data"]:
                continue
            setattr(self, key, val)
        if "childs" in treedict.keys():
            for _childdict in treedict["childs"]:
                # https://stackoverflow.com/questions/17959996/get-python-class-object-from-class-name-string-in-the-same-module
                if "_clsname" in _childdict["data"] and _childdict["data"]["_clsname"]:
                    _nodecls = getattr(sys.modules[__name__], _childdict["data"]["_clsname"])
                    _nodecls(parent=self, treedict=_childdict)
                else:
                    self.__class__(parent=self, treedict=_childdict)



class CallNode(Loadcase):
    _return = NodeAttr()
    _arguments = NodeAttr()
    _callfuncname = NodeAttr()

    def __init__(self, name=None, parent=None, parameters=None, pyfile=None,
                data=None, treedict=None, callfunc=None):
        super().__init__(name, parent, data=data, treedict=treedict,
                        parameters=parameters)
        #self._callfunc = None
        #self._return = None
        #self._arguments = None
        self._df = None
        if callfunc:
            self.set_callfunc(callfunc)
        ##self._clsname = self.__class__.__name__
        self._result_attr = True

    @property
    def _callfunc(self):
        return getattr(self, self._callfuncname, None)


    def __call__(self, add_child=False, *args, **kwargs):
        # if not self._callfuncname:
        #     return None
        # #_func = getattr(self, self._callfuncname)
        # _func = self._callfunc
        if self._callfunc is None:
            return None
        _ret = self._callfunc(*args, **kwargs)
        self._return = _ret
        return _ret


    def set_callfunc(self, callfunc):
        if isinstance(callfunc, str) and hasattr(self, callfunc):
            self._callfuncname = callfunc
        elif callable(callfunc) and hasattr(callfunc, "__name__") and hasattr(self, callfunc.__name__):
            self._callfuncname = callfunc.__name__
        else:
            logger.warning("%s.set_callfunc: «%s» arg «callfunc»=«%s» not correctly specified." % (self.__class__.__name__, self.name, callfunc))

    def call_child(self, call=False, name=None, **kwargs):
        if kwargs:
            _parameters = dict(kwargs)
        else:
            _parameters = None
        # if name is None:
        #     name = "{} c{}".format(self._callfuncname, len(self.childs))
        _nodedata = copy.deepcopy(self.data)
        _nodedata["_arguments"] = None
        _nodedata["_return"] = None
        _nodedata["name"] = name
        _child = self.__class__(parent=self, data=_nodedata, parameters=_parameters)
        if call:
            _child()
        return _child

    # def to_df(self, norepeat=False, keep=False):
    #     # df = pd.DataFrame(data={**self._arguments, **self._return})
    #     if (not pandas_imported or (self._callfuncname is None) 
    #         or (self._return is None) ):
    #         return None
    #     if "return" in self._callfunc._argmap:
    #         _ident = self._callfunc._argmap["return"]
    #     else:
    #         _ident = self._callfunc.__name__
    #     if isinstance(self._return, dict):
    #         _df = pd.DataFrame()
    #         # for _k, _v in self._return.items():
    #         #     if isinstance(_v, np.ndarray):
    #         #         if len(_v) == len(_df):
    #         #             _df.insert(0, _k, _v)
    #         #     else:
    #         #         _df.insert(0, _k, [_v]*len(_df))
    #         for _k, _v in self._return.items():
    #             if isinstance(_v, np.ndarray):
    #                 _df.insert(len(_df.columns), _k, _v)
    #         for _k, _v in self._return.items():
    #             if _k in list(_df.columns.values):
    #                 continue
    #             _df.insert(len(_df.columns), _k, [_v]*len(_df))
    #     elif isinstance(self._return, np.ndarray):
    #         _df = pd.DataFrame(self._return, columns=[_ident])
    #     elif isinstance(self._return, (list, tuple)):
    #         _df = pd.DataFrame([self._return], columns=[_ident+str(i) for i in range(len(self._return))])
    #     else:
    #         _df = pd.DataFrame([self._return], columns=[_ident])
    #     for _k, _v in reversed(self._arguments.items()):
    #         if _k in list(_df.columns.values):
    #             continue
    #         if isinstance(_v, np.ndarray):
    #             if len(_v) == len(_df):
    #                 #self._df[_k] = _v
    #                 _df.insert(0, _k, _v)
    #         else:
    #             _df.insert(0, _k, [_v]*len(_df))
    #     # https://stackoverflow.com/questions/20209600/pandas-dataframe-remove-constant-column
    #     if norepeat and len(_df)>1:
    #         _df = _df.loc[:, (_df != _df.iloc[0]).any()]
    #     if keep:
    #         self._df = _df
    #     return _df

    # def to_hdf(self, path=None, key=None, append=True):
    #     if self._return is None:
    #         logger.error("%s.to_hdf: node «%s» not called." % (self.__class__.__name__, self.name))
    #         return None
    #     if not self._df:
    #         self.to_df(keep=True)
    #     if key:
    #         _key = key
    #     else:
    #         _key=self.nodepath
    #     self._df.to_hdf(path, _key, format="table", data_columns=True,
    #                     append=append, mode="a")


    def to_df(self, return_df=True):
        if self._arguments and self._return:
            self._df = pd.DataFrame(data={**self._arguments, **self._return})
        else:
            self._df = None
        if return_df:
            return self._df


    def to_hdf(self, hdf_fpath=None, key=None, append=False):
        if self._return is None:
            logger.error("%s.to_hdf: node «%s» not called." % (self.__class__.__name__, self.name))
            return None
        if hdf_fpath:
            _fpath = hdf_fpath
        else:
            _fpath = self._hdf_fpath
        if _fpath is None:
            logger.error("%s.to_hdf: arg `_fpath`=«%s» not correct." % (self.__class__.__name__, _fpath))
            return None
        if key:
            _key = key
        else:
            _key = self._path
        if self._df is None:
            self.to_df(return_df=False)
        self._df.to_hdf(_fpath, _key, format="table", data_columns=True,
                        append=append, mode="a")
    






if __name__ == "__main__":
    pass
    
    

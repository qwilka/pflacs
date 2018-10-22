"""
Copyright © 2018 Stephen McEntee
Licensed under the MIT license. 
See «pflacs» LICENSE file for details:
https://github.com/qwilka/pflacs/blob/master/LICENSE
"""
from types import ModuleType  # MethodType
import functools
import inspect
import copy
#import sys
#import os
#import string
#import ast
import re
import logging
#import time
#from traceback import extract_stack
logger = logging.getLogger(__name__)

from vntree import Node    #, TreeAttr

#valid_identifier = re.compile(r"^[^\d\W]\w*$", re.UNICODE)
#re.compile(r'^_*[a-zA-Z][_0-9a-zA-Z]*$')
#[_a-zA-Z]\w*

logger.debug("#### in pflacs.py: DEBUG this is a test  ####")


class Parameter:
    """NOTE this class is not related to Python's inspect.Parameter """
    def __init__(self, name=None):
        logger.debug("Parameter.__init__ «name» {}".format(name, ))
        self.name = name
    def __get__(self, instance, owner):
        logger.debug("Parameter.__get__ «instance» {}, «owner» {}".format(instance, owner))
        if instance:
            _param_val = instance.data["params"].get(self.name, False)
            if not _param_val and instance.parent:
                logger.debug("Parameter.__get__ «instance.parent» {}".format(instance.parent, ))
                _param_val = instance.parent.data["params"].get(self.name, False)
        elif owner:
            _param_val = owner.data["params"].get(self.name, False)
        else:
            _param_val = False
        return _param_val
    def __set__(self, instance, value):
        if instance:
            logger.debug("Parameter.__set__ «name» {} «value» {} set on «instance» {}.".format(self.name, value, instance))
            instance.data["params"][self.name] = value
        else:
            logger.debug("Parameter.__set__ «name» {} «value» {} called at class level.".format(self.name, value))
    def __delete__(self, instance):
        # don't delete at class level, in case another instance is using this attribute
        #_param_val = instance.params.pop(self.name)
        del instance.data["params"][self.name]
        #delattr(instance, self.name)
    def __set_name__(self, owner, name):
        logger.debug("Parameter.__set_name__ «self» {} «owner» {} «name» {}".format(self, owner, name))
        self.name = name


class Function:
    def __init__(self, func, argmap=None):
        self.name = func.__name__
        self._sig = inspect.signature(func)
        self._func = func
        # if not isinstance(argmap, (dict, None)):
        #     raise TypeError('Function: argument «argmap» not correctly specified.')
        if isinstance(argmap, dict):
            self.argmap = argmap
        else:
            self.argmap = {}
        self._instance = None
    def __get__(self, instance, owner):
        logger.debug("Function.__get__ «instance» {}, «owner» {}".format(instance, owner))
        self._instance = instance
        return self
    def __call__(self, *args, **kwargs):
        #_xkwargs = {}
        logger.debug("Function.__call__: function «%s».«%s»; args «%s»; kwargs «%s»" % (self._instance, self.name, args, kwargs))
        _xkwargs = copy.deepcopy(kwargs)
        for ii, (_key, _para) in enumerate(self._sig.parameters.items()):
            logger.debug("Function.__call__: function «%s».«%s»; parameter name «%s»" % (self._instance, self.name, _para.name))
            if ii<len(args):
                continue
            if _para.name in self.argmap and self.argmap[_para.name] in kwargs:
                _parval = _xkwargs.pop(self.argmap[_para.name])
                _xkwargs[_para.name] = _parval
            elif _para.name in kwargs:
                logger.debug("Function.__call__: WARNING «%s».«%s»; parameter name «%s» is keyword argument in original function «%s» (binding nonetheless)." % (self._instance, self.name, _para.name, self._func.__name__))
                continue
            if self.argmap and _para.name in self.argmap.keys():
                _inst_param = self.argmap[_para.name]
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
                if _argname in self.argmap:
                    _argname = self.argmap.get(_argname)
                    _argname = "missing parameter «{}»".format(_argname)
            logger.error("Function.__call__: function «%s».«%s»; %s; (original function error: %s)" % (self._instance, self.name, _argname, err))
            return False
        return self._func(*_bound.args, **_bound.kwargs)



class Loadcase(Node):
    #params = {}
    #XX = Parameter2()

    def __init__(self, name, parent=None, params=None, pyfile=None,
                data=None, treedict=None):
        super().__init__(name, parent, data)
        #self.set_data("params", value={})
        if "params" in self.data and isinstance(self.data["params"], dict):
            _pars = copy.deepcopy(self.data["params"])
            if params and isinstance(params, dict):
                _pars.update(copy.deepcopy(params))
            params = _pars
        self.data["params"] =  {}
        if params and isinstance(params, dict):
            self.import_params(params)
        
        # else:
        #     self.data.params = {}
        if pyfile:
            self.import_params_pyfile(pyfile)

    def add_param(self, name, value=None):
        if name in self.data["params"]:
            logger.debug("add_param: {} is already param of «{}»!".format(name, self.name))
        else:
            setattr(self.__class__, name, Parameter(name))
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
        for _key, _val in params.items():
            if callable(_val) or isinstance(_val, ModuleType):
                continue
            self.add_param(_key, _val)
        return True

    def import_params_pyfile(self, pyfile):
        gbl_var={}; loc_var={}
        try:
            exec(compile(open(pyfile).read(), pyfile, 'exec'), gbl_var, loc_var)
        except Exception as err:
            logger.error("LoadcaseNode.import_params_pyfile: cannot import parameters from file %s; %s" % (pyfile, err))
            return False
        return self.import_params(loc_var)

    @classmethod
    def import_function(cls, function, argmap=None):
        """Class method for importing a function into a class. """
        logger.info("Loadcase.import_function importing {} into {}.".format(function.__name__, cls))
        # test if «function» is valid for Pflacs:
        try:
            _sig = inspect.signature(function)
        except (ValueError, TypeError) as err:
            logger.error("LoadcaseNode.import_function: function «%s» is not valid for Pflacs: %s" % (function, err))
            return False
        setattr(cls, function.__name__, Function(function, argmap=argmap))
        functools.update_wrapper(getattr(cls, function.__name__), function)
        return True



if __name__ == "__main__":
    pass
    
    

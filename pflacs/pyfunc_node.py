"""

https://python-reference.readthedocs.io/en/latest/docs/functions/apply.html
"""
from datetime import datetime, timezone
import importlib
import inspect
import logging
import subprocess

logger = logging.getLogger(__name__)

from .pflacs import Premise, NodeAttr, _empty


class PyFunc(Premise):
    """Class for creating nodes that call a Python function.

    :class:`PyFunc` is a sub-class of :class:`Premise`.

    :param name: node name
    :type name: str or None
    :param parent: The parent node of this node.
    :type parent: Node or None
    :param parameters: dictionary of input parameters.
    :type parameters: dict or None
    :param data: Dictionary containing node data.
    :type data: dict or None
    :param treedict: Dictionary specifying a complete tree.
    :type treedict: dict or None
    :param funcname: name of `pflacs` plugin funcion/module to be used dby this calculation node.
    :type funcname: str or None
    :param argmap: optional mapping for names of function arguments and return values.
    :type argmap: dict or None
    """
    #_internals = NodeAttr(initial={})
    #_arguments = NodeAttr()
    _funcname = NodeAttr()
    _argmap = NodeAttr()
    _kwargs = NodeAttr()
    #_stdout = NodeAttr()
    #_stderr = NodeAttr()
    _timestamp = NodeAttr("vn")

    def __init__(self, name=None, parent=None, parameters=None,
                data=None, treedict=None, function=None, 
                argmap=None, kwargs=None):
        super().__init__(name, parent, data=data, treedict=treedict,
                        parameters=parameters)
        self._df = None
        if treedict is None:
            self._return2attr = True
        self._argmap = None
        if treedict is None or isinstance(argmap, dict):
            self._argmap = argmap
        if treedict is None or isinstance(kwargs, dict):
            self._kwargs = kwargs
        #if function:
            # if callable(function):
            #     self._function = (function.__name__, function.__module__)
            # else:
            #     logger.error("%s.__init__: argument «function» must be callable, «%s» is %s." % (self.__class__.__name__, function, type(function)))
        self.plugin_func(function)


    def plugin_func(self, function=None):
        """Plugin a Python function that will be called on this node
        instance specifically (not patched into class).
        """
        if function:
            if callable(function):
                self._funcname = (function.__name__, function.__module__)
                self._function = function
            else:
                logger.error("%s.plugin_func: argument «function» must be callable, «%s» is %s." % (self.__class__.__name__, function, type(function)))
        else:
            _mod = importlib.import_module(self._funcname[1])
            self._function = getattr(_mod, self._funcname[0])
        _sig = inspect.signature(self._function)
        self._req_args = []
        self._req_kwargs = []
        for _param in _sig.parameters.values():
            if self._argmap and _param.name in self._argmap:
                _pname = self._argmap[_param.name]
            else:
                _pname = _param.name
            if (_param.kind == inspect.Parameter.POSITIONAL_ONLY):
                self._req_args.append(_pname)
            else:
                self._req_kwargs.append(_pname)

        #setattr(self, _methodname, _function)


    def __call__(self, *args, **kwargs):
        _args = list(args)
        for ii, _argname in enumerate(self._req_args):
            if ii<len(args): continue
            if self._kwargs and _argname in self._kwargs:
                _args.append(self._kwargs[_argname])
            elif self.is_param(_argname):
                _args.append( getattr(self, _argname))
        _xkwargs = self._kwargs.copy() if self._kwargs else {}
        if kwargs:
            _xkwargs.update(kwargs)
        # for _k in self._req_kwargs:
        #     if _k in _xkwargs: continue
        #     _xkwargs[_k] = getattr(self, _k)
        for _k, _v in _xkwargs.items():
            if _v is _empty:
                _xkwargs[_k] = getattr(self, _k)
        _ret = self._function(*_args, **_xkwargs)
        return _ret
        # print(f"{self.__class__.__name__}:{self.name} args={args}")
        # print(f"{self.__class__.__name__}:{self.name} _xkwargs={_xkwargs}")
        # self._stdout = self._stderr = ""
        # self._timestamp = [datetime.utcnow().replace(tzinfo=timezone.utc).timestamp(), None]
        # # datetime.utcfromtimestamp(timestamp).isoformat()
        # try:
        #     #op = subprocess.run(self._cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        #     op = subprocess.run(self._cmd, capture_output=True) # , capture_output=True
        # #except subprocess.CalledProcessError as err:
        # except Exception as err:
        #     self._stderr = op.stderr.decode('UTF-8')
        #     logger.error("%s.__call__: node «%s» cannot process %s: %s : %s." % (self.__class__.__name__, self.name, self._cmd, err, self._stderr))
        # self._timestamp[1] = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()
        # self._stdout = op.stdout.decode('UTF-8')
        # print(f"SubProc {self.name}: op={self._stdout}")

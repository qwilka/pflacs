from datetime import datetime, timezone
import logging
import subprocess

logger = logging.getLogger(__name__)

from .pflacs import Premise, NodeAttr


class SubProc(Premise):
    """Class for creating subprocess.run nodes.

    :class:`SubProc` is a sub-class of :class:`Premise`.

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
    #_funcname = NodeAttr()
    #_argmap = NodeAttr()
    _cmd = NodeAttr()
    _kwargs = NodeAttr()
    _stdout = NodeAttr()
    _stderr = NodeAttr()
    _timestamp = NodeAttr("vn")

    def __init__(self, name=None, parent=None, parameters=None,
                data=None, treedict=None, cmd=None, 
                kwargs=None, shell=False):
        super().__init__(name, parent, data=data, treedict=treedict,
                        parameters=parameters)
        self._df = None
        #self._funcname = funcname
        # if treedict is None or funcname:
        #     self._funcname = funcname
        #self._return2attr = True
        if treedict is None:
            self._return2attr = True
        #self._argmap = None
        # if treedict is None or isinstance(argmap, dict):
        #     self._argmap = argmap
        if treedict is None or isinstance(kwargs, dict):
            self._kwargs = kwargs
        if cmd is not None:
            self._cmd = cmd



    def __call__(self, *args, **kwargs):
        _xkwargs = self._kwargs.copy() if self._kwargs else {}
        if kwargs:
            _xkwargs.update(kwargs)
        print(f"{self.__class__.__name__}:{self.name} args={args}")
        print(f"{self.__class__.__name__}:{self.name} _xkwargs={_xkwargs}")
        self._stdout = self._stderr = ""
        self._timestamp = [datetime.utcnow().replace(tzinfo=timezone.utc).timestamp(), None]
        # datetime.utcfromtimestamp(timestamp).isoformat()
        try:
            #op = subprocess.run(self._cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            op = subprocess.run(self._cmd, capture_output=True) # , capture_output=True
        #except subprocess.CalledProcessError as err:
        except Exception as err:
            self._stderr = op.stderr.decode('UTF-8')
            logger.error("%s.__call__: node «%s» cannot process %s: %s : %s." % (self.__class__.__name__, self.name, self._cmd, err, self._stderr))
        self._timestamp[1] = datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()
        self._stdout = op.stdout.decode('UTF-8')
        print(f"SubProc {self.name}: op={self._stdout}")

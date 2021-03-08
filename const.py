"""This class is in charge for making const running"""
import sys
class _const:
    """Rewrite const"""
    class ConstError(TypeError):
        """Skip error"""
        pass
    def __setattr__(self,name,value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const (%s)" %name)
        self.__dict__[name]=value

sys.modules[__name__]=_const()

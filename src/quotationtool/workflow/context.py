from zope.interface import implements
from zope.wfmc.interfaces import IProcessContext

class Context(object):

    implements(IProcessContext)

    def processFinished(self, process, *result):
        pass

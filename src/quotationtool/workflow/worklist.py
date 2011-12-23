import zope.interface
from zope.container.btree import BTreeContainer
from zope.container.interfaces import INameChooser
from zope.container.contained import NameChooser
import datetime

from quotationtool.workflow import interfaces


class WorkList(BTreeContainer):

    zope.interface.implements(interfaces.IWorkList)

    __name__ = __parent__ = None

    def pop(self):
        return self[self.keys()[-1]]

    def append(self, obj):
        name = INameChooser(self).chooseName(None, obj)
        self[name] = obj

    def remove(self, obj):
        del self[obj.__name__]


class WorkItemNameChooser(NameChooser):

    zope.interface.implements(INameChooser)
    zope.component.adapts(interfaces.IWorkList)

    def chooseName(self, name, obj):
        """ choose timestamp as name."""
        now = unicode(datetime.datetime.now())
        return super(WorkItemNameChooser, self).chooseName(now, obj)

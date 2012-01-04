import zope.interface
from z3c.menu.ready2go.item import ContextMenuItem


class IWorkflowTab(zope.interface.Interface): pass
class WorkflowTab(ContextMenuItem):
    zope.interface.implements(IWorkflowTab)

import zope.interface
from zope.container.btree import BTreeContainer

from quotationtool.workflow import interfaces


class WorkFlowContainer(BTreeContainer):
    """ Implementation of the container that contains all workflow
    related things."""

    zope.interface.implements(interfaces.IWorkFlowContainer)

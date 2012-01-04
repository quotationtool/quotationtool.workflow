import zope.interface
import zope.component
from zope.viewlet.manager import ViewletManager
from z3c.menu.ready2go import ISiteMenu
from z3c.menu.ready2go.manager import MenuManager

from quotationtool.skin.interfaces import ISubNavManager
from quotationtool.skin.browser.nav import MainNavItem


class IWorkFlowContainerMainNavItem(zope.interface.Interface): 
    """ A marker interface for the workflow nav item in the main navigation."""
    pass


class WorkFlowContainerMainNavItem(MainNavItem):
    """The workflow navigation item in the main navigation."""

    zope.interface.implements(IWorkFlowContainerMainNavItem)


class IWorkFlowContainerSubNav(ISubNavManager):
    """A manager for the workflow subnavigation."""

WorkFlowContainerSubNav = ViewletManager('workflowcontainersubnav',
                                        ISiteMenu,
                                        bases = (MenuManager,))

IWorkFlowContainerSubNav.implementedBy(WorkFlowContainerSubNav)

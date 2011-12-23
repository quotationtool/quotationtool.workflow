import zope.component
from zope.interface import implements, Interface
from z3c.table import table, column
from z3c.table.interfaces import ITable
from z3c.pagelet.browser import BrowserPagelet
from zope.authentication.interfaces import IAuthentication
from zope.dublincore.interfaces import IZopeDublinCore

from quotationtool.workflow.interfaces import _


class ListWorkLists(BrowserPagelet):
    """ Pagelet on workflow container."""

    def lists(self):
        return self.context.values()


class IWorkListTable(ITable):
    """ A list of work items (table for worklist container)."""


class WorkListTable(table.Table, BrowserPagelet):
    """ The bibliography printed like a table."""

    zope.interface.implements(IWorkListTable)

    render = BrowserPagelet.render

    cssClasses = {
        'table': u'container-listing',
        'thead': u"head",
        }
    cssClassEven = u"even"
    cssClassOdd = u"odd"

    def title(self):
        return getattr(IZopeDublinCore(self.context, None), 'title', u'Unkown')

    def description(self):
        return getattr(IZopeDublinCore(self.context, None), 'description', u'Unkown')


class ISortingColumn(Interface):
    """ A sorting column."""


class ProcessColumn(column.Column):

    implements(ISortingColumn)

    header = _('process-column-header', u"Process")
    weight = 100

    def renderCell(self, item):
        proc = item.participant.activity.process
        definition = getattr(proc.definition)
        return definition.__name__


class WorkItemColumn(column.Column):

    implements(ISortingColumn)

    header = _('workitem-column-header',
               u"Work Item")
    weight = 110

    def renderCell(self, item):
        # makes sense to use label view because we need it in other
        # contexts
        view = zope.component.getMultiAdapter(
            (item, self.request),
            name='label')
        return view()


class ContributorColumn(column.Column):

    implements(ISortingColumn)

    header = _('contributor-column-header', u"Contributor")
    weight = 200

    def renderCell(self, item):
        contributor = getattr(item.participant.activity.process.workflowRelevantData, 'contributor', u'Unkown')
        pau = zope.component.queryUtility(
            IAuthentication,
            context = self.context
            )
        if pau is not None:
            try:
                contributor = pau.getPrincipal(list(contributor)[0]).title
            except Exception:
                pass
        return contributor


class LastActivityByColumn(column.Column):
    """ The dc creator of a work item is the one who performed the
    last activity in the workflow."""

    zope.interface.implements(ISortingColumn)

    header = _('last-activity-by-column-header',
               u"Last Activity By")
    weight = 210
    
    def renderCell(self, item):
        creator = u"Unkown"
        dc = IZopeDublinCore(item, None)
        if dc is None:
            return creator
        pau = zope.component.queryUtility(
            IAuthentication,
            context = self.context
            )
        if pau is not None:
            try:
                creator = pau.getPrincipal(dc.creators[0]).title
            except Exception:
                pass
        return creator


class DCSortingColumn(object):
    """Mixin class for sorting unformatted dublincore values."""

    def getSortKey(self, item):
        dc = IZopeDublinCore(item, None)
        return self.getValue(dc)


class LastActivityColumn(column.LinkColumn):
    """Column representing the dublincore created value. """

    zope.interface.implements(ISortingColumn)

    header = _('last-activity-column-header',
               u"Last Activity")

    weight = 220

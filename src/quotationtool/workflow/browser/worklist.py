import zope.component
from zope.interface import implements, Interface
from z3c.table import table, column, value
from z3c.table.interfaces import ITable
from z3c.pagelet.browser import BrowserPagelet
from zope.authentication.interfaces import IAuthentication
from zope.dublincore.interfaces import IZopeDublinCore
from zope.publisher.browser import BrowserView
from zope.i18n import translate
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from z3c.formui import form
from z3c.indexer.search import SearchQuery
from z3c.indexer.query import AnyOf

from quotationtool.user.interfaces import IAccountView

from quotationtool.workflow.interfaces import _
from quotationtool.workflow import interfaces


class ListWorkLists(BrowserPagelet):
    """ Pagelet on workflow container."""

    def lists(self):
        return self.context.values()

class WorkFlowContainerLabel(BrowserView):
    """ A label for the workflow container."""

    def __call__(self):
        return _(u"Workflow")


class WorkListLabel(BrowserView):
    """ A label for the workflow container."""

    def __call__(self):
        return getattr(IZopeDublinCore(self.context, None), 'title', _(u"Work list"))


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
        return getattr(IZopeDublinCore(self.context, None), 'title', self.context.__name__)

    def description(self):
        return getattr(IZopeDublinCore(self.context, None), 'description', u"")


class SimilarWorkItemsTable(table.Table, BrowserView):
    
    zope.interface.implements(IWorkListTable)

    template = ViewPageTemplateFile('similar_work_items.pt')

    cssClasses = {
        'table': u'container-listing',
        'thead': u"head",
        }
    cssClassEven = u"even"
    cssClassOdd = u"odd"

    def __call__(self):
        self.update()
        return self.template()


class SimilarWorkItemsValues(value.ValuesMixin):

    @property
    def values(self):
        similars = interfaces.ISimilarWorkItems(self.context)
        return similars.getSimilarWorkItems()


class AccountWorkListTable(table.Table, BrowserPagelet):
    """ The bibliography printed like a table."""

    zope.interface.implements(IWorkListTable, IAccountView)

    render = BrowserPagelet.render

    cssClasses = {
        'table': u'container-listing',
        'thead': u"head",
        }
    cssClassEven = u"even"
    cssClassOdd = u"odd"

    @property
    def title(self):
        return _('account-worklist-title', u"Work Items ($COUNT)",
                 mapping={'COUNT': unicode(self.getCount())})

    description = _('account-worklist-desc', u"Items saved as 'draft' and other items on your personal to-do list.")

    visible = True

    weight = 10

    def getCount(self):
        return len(list(self.values))


class AccountValues(value.ValuesMixin):
    """ Values for the account table."""

    @property
    def values(self):
        principal_id = self.request.principal.id
        query = SearchQuery(AnyOf('workitem-contributors', (principal_id,)))
        return query.searchResults()


class ISortingColumn(Interface):
    """ A sorting column."""


class ProcessStartedColumn(column.Column):

    implements(ISortingColumn)

    header = _('processstarted-column-header',
               u"Process Started")
    weight = 90

    def renderCell(self, item):
        return getattr(item, 'starttime', _(u"Unknown"))


class ProcessColumn(column.Column):

    implements(ISortingColumn)

    header = _('process-column-header', u"Process")
    weight = 100

    def renderCell(self, item):
        return interfaces.IWorkflowInfo(item).process_name


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
        rc = view()
        try:
            rc = translate(rc, context=self.request)
        except Exception:
            pass
        return rc


class ContributorColumn(column.Column):

    implements(ISortingColumn)

    header = _('contributor-column-header', u"Started By")
    weight = 105

    def renderCell(self, item):
        contributor = getattr(item, 'contributor', u'Unkown')
        pau = zope.component.queryUtility(
            IAuthentication,
            context = self.context
            )
        try:
            contributor = pau.getPrincipal(contributor).title
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


class ObjectLabelColumn(column.Column):
    """Column displaying the label of the object under workflow
    control."""

    zope.interface.implements(ISortingColumn)

    header = _('object-column-header',
               u"Database item")
    weight = 108

    def renderCell(self, item):
        obj = getattr(item, 'object_', None)
        if obj is None:
            return _(u"Unkown")
        label =  zope.component.getMultiAdapter(
            (obj, self.request), name='label')()
        try:
            return translate(label, context=self.request)
        except Exception:
            return label


class EditMeta(form.EditForm):

    fields = field.Fields(IZopeDublinCore).select('title', 'description')

    label = _('edit-meta-label', u"Metadata")

    info = _('edit-meta-info',
             u"You can edit the descriptive metadata of the worklist.")

    def getContent(self):
        return IZopeDublinCore(self.context, None)


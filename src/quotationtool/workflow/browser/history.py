from zope.interface import implements
import zope.component
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from z3c.pagelet.browser import BrowserPagelet
from zope.authentication.interfaces import IAuthentication
from cgi import escape
from z3c.table import table, value
from z3c.indexer.query import AnyOf
from z3c.indexer.search import SearchQuery
from zope.intid.interfaces import IIntIds

from quotationtool.skin.interfaces import ITabbedContentLayout

from quotationtool.workflow.interfaces import IWorkflowHistory
from quotationtool.workflow.browser.worklist import IWorkListTable


class NotationBaseView(BrowserView):

    cssClass = u'notation'

    template = ViewPageTemplateFile('notation.pt')

    def __call__(self):
        return self.template()


class ProcessStarted(NotationBaseView):

    cssClass = u'notation process-started'


class ProcessFinished(NotationBaseView):

    cssClass = u'notation process-finished'


class ActivityStarted(NotationBaseView):

    cssClass = u'notation activity-started'


class ActivityFinished(NotationBaseView):

    cssClass = u'notation activity-finished'


class WorkItemFinished(NotationBaseView):

    cssClass = u'notation workitem-finished'


class Transition(NotationBaseView):

    cssClass = u'notation transition'


class UserNotation(NotationBaseView):

    template = ViewPageTemplateFile('usernotation.pt')

    cssClass = u'notation user-notation'

    def name(self):
        user = getattr(self.context, 'uid', u'Unkown')
        pau = zope.component.queryUtility(
            IAuthentication,
            context = self.context
            )
        try:
            user = pau.getPrincipal(user).title
        except Exception:
            pass
        return user

    def message(self):
        return escape(self.context.msg).replace('\n', '<br/>\n')


class WorkflowHistory(table.Table, BrowserPagelet):
    """ A pagelet presenting the workflow history of an item
    implementing IHasWorkflowHistory"""

    implements(IWorkListTable, ITabbedContentLayout)

    cssClasses = {
        'table': u'container-listing',
        'thead': u"head",
        }
    cssClassEven = u"even"
    cssClassOdd = u"odd"

    render = BrowserPagelet.render

    def notations(self):
        history = IWorkflowHistory(self.context)
        return history.reverse()


class CurrentWorkItemsValues(value.ValuesMixin):
    """ Adapter to get table values."""

    @property
    def values(self):
        intids = zope.component.getUtility(IIntIds, context=self.context)
        oid = intids.queryId(self.context)
        if oid:
            query = SearchQuery(AnyOf('workflow-relevant-oids', [oid]))
            res = query.apply()
            #raise Exception(res)
            for intid in res:
                    yield intids.getObject(intid)


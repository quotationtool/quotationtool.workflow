import zope.interface
import zope.component
from persistent import Persistent
from zope.location.location import Location
from zope.wfmc.interfaces import IWorkItem, IParticipant, ProcessError
from zope.app.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from z3c.indexer.interfaces import IIndex, IIndexer
from z3c.indexer.query import AnyOf
from z3c.indexer.search import SearchQuery
from z3c.indexer.indexer import ValueIndexer
from zope.intid.interfaces import IIntIdAddedEvent, IIntIdRemovedEvent

from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _


class WorkItemBase(Persistent, Location):

    zope.interface.implements(IWorkItem)
    zope.component.adapts(IParticipant)

    worklist = 'undefined'

    schema = None

    def __init__(self, participant):
        self.participant = participant

    def _appendToWorkList(self):
        worklist = zope.component.getUtility(
            interfaces.IWorkList,
            name=self.worklist,
            context=getSite())
        worklist.append(self)

    def _removeFromWorkList(self):
        worklist = zope.component.getUtility(
            interfaces.IWorkList,
            name=self.worklist,
            context=getSite())
        worklist.remove(self)

    @property
    def worklist(self):
        return self.participant.__name__


class ContributorWorkItem(WorkItemBase):

    #worklist = 'contributor'

    schema = interfaces.IEditSchema

    def start(self):
        self._appendToWorkList()

    def finish(self, save):
        self.schema['save'].validate(save)
        # we remove the work item on save=='draft', too. It gets added by start again.
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, save)


class EditorialReviewWorkItem(WorkItemBase):

    #worklist = 'editor'

    schema = interfaces.IEditorialReviewSchema

    def start(self):
        self._appendToWorkList()

    def finish(self, publish):
        self.schema['publish'].validate(publish)
        # we remove the work item on publish=='postpone', too. It gets
        # added by start again.
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, publish)


class WorkflowInfo(object):
    """ Adapter that offers information about the workflow process
    which a work item is part of."""

    zope.interface.implements(interfaces.IWorkflowInfo)
    zope.component.adapts(IWorkItem)

    def __init__(self, context):
        self.context = context
        self.participant = getattr(context, 'participant', None)
        self.activity = getattr(self.participant, 'activity', None)
        self.process = getattr(self.activity, 'process', None)
        self.process_definition = getattr(self.process, 'definition', None)

    @property
    def process_name(self):
        return getattr(self.process_definition, '__name__', _(u"Unkown"))
        

class SimilarWorkItemsMixin(object):
    """ See ISimilarWorkItems"""

    zope.interface.implements(interfaces.ISimilarWorkItems)

    oid_attributes = ()

    def getSimilarWorkItems(self):
        ids = []
        intids = zope.component.getUtility(IIntIds, context=self)
        for attr in self.oid_attributes:
            intid = intids.queryId(getattr(self, attr), None)
            if intid is not None:
                ids.append(intid)
        #raise Exception(ids)
        query = SearchQuery(AnyOf('workflow-relevant-oids', ids))
        res = query.apply()
        #raise Exception(res)
        for intid in res:
            if intid != intids.getId(self):
                yield intids.getObject(intid)


class OIDsIndexer(ValueIndexer):
    """ Returns object ids of the object under workflow control."""

    #zope.component.adapts(interfaces.ISimilarWorkItems)    
    #zope.component.adapts(IWorkItem)

    indexName = 'workflow-relevant-oids'

    @property
    def value(self):
        ids = []
        intids = zope.component.getUtility(IIntIds, context=self.context)
        for attr in self.context.oid_attributes:
            i = intids.queryId(getattr(self.context, attr, None))
            if i:
                ids.append(i)
        return ids

    def doIndexOFF(self):
        raise Exception


@zope.component.adapter(IIntIdAddedEvent)
def indexOIDs(event):
    indexer = zope.component.queryAdapter(
        event.object, IIndexer, 
        name='workflow-relevant-oids')
    if indexer:
        indexer.doIndex()


@zope.component.adapter(IIntIdRemovedEvent)
def unindexOIDs(event):
    indexer = zope.component.queryAdapter(
        event.object, IIndexer, 
        name='workflow-relevant-oids')
    if indexer:
        indexer.doUnIndex()



import zope.interface
import zope.component
from persistent import Persistent
from zope.location.location import Location
from zope.wfmc.interfaces import IWorkItem, IParticipant, ProcessError
from zope.app.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from z3c.indexer.interfaces import IIndex, IIndexer
from z3c.indexer.query import AnyOf, Eq
from z3c.indexer.search import SearchQuery
from z3c.indexer.indexer import ValueIndexer
from zope.intid.interfaces import IIntIdAddedEvent, IIntIdRemovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.dublincore.interfaces import IZopeDublinCore
from zope.security.management import queryInteraction
from zope.security.proxy import removeSecurityProxy

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
        

class SimilarWorkItemsBase(object):
    """ An base class for builing adapters. """

    zope.interface.implements(interfaces.ISimilarWorkItems)

    def __init__(self, context):
        self.context = context

    def getSimilarWorkItems(self):
        """ See ISimilarWorkItems"""
        ids = []
        intids = zope.component.getUtility(IIntIds, context=self.context)
        for obj in self.objects:
            intid = intids.queryId(obj, None)
            if intid is not None:
                ids.append(intid)
        #raise Exception(ids)
        query = SearchQuery(AnyOf('workflow-relevant-oids', ids))
        res = query.apply()
        #raise Exception(res)
        for intid in res:
            if intid != intids.getId(self.context):
                #raise Exception(intid)
                yield intids.getObject(intid)

    @property
    def objects(self):
        """ See ISimilarWorkItems"""
        raise NotImplemented


class SimilarWorkItemsByObjectAttribute(SimilarWorkItemsBase):
    """ SimilarWorkItems for workitems where the relevant database
    item lives on the object_ attribute."""

    @property
    def objects(self):
        obj = getattr(self.context, 'object_', None)
        if obj:
            return (obj,)
        return ()


class OIDsIndexerBase(ValueIndexer):
    """ Base class for building indexers that index the IDs of
    database items relevant for the workflow process/workitem in
    context.

    objects needs to be defined. It should return the database items
    relevant for the workitem in context."""

    indexName = 'workflow-relevant-oids'

    @property
    def value(self):
        ids = []
        intids = zope.component.getUtility(IIntIds, context=self.context)
        for obj in self.objects:
            i = intids.queryId(obj)
            if i:
                ids.append(i)
        return ids

    @property
    def objects(self):
        raise NotImplemented


class OIDsIndexerByObjectAttribute(OIDsIndexerBase):
    """ Indexes oids for workitems where the relevant database
    item lives on the object_ attribute.

    Needs to be registered for specific work items."""

    @property
    def objects(self):
        obj = getattr(self.context, 'object_', None)
        if obj:
            return (obj,)
        return ()


class OIDsIndexerByContextItem(OIDsIndexerBase):
    """ Indexes oids for workitems where the relevant database item
    lives on the 'item' attribute of the process context.

    Needs to be registered for specific work items."""

    @property
    def objects(self):
        participant = getattr(self.context, 'participant', None)
        activity = getattr(participant, 'activity', None)
        process = getattr(activity, 'process', None)
        context = getattr(process, 'context', None)
        item = getattr(process, 'context', None)
        if item: 
            return (item,)
        return ()


class ProcessIdIndexer(ValueIndexer):
    """ Indexes the process id for work items."""

    indexName = 'workitem-processid'

    @property
    def value(self):
        participant = getattr(self.context, 'participant', None)
        activity = getattr(participant, 'activity', None)
        process = getattr(activity, 'process', None)
        definition = getattr(process, 'definition', None)
        #raise Exception(getattr(definition, 'id', None))
        return getattr(definition, 'id', None)
        

def findWorkItemsForItemAndProcessId(item, process_id):
    """ Returns workitems for 'item' 'process_id'."""
    intids =zope.component.getUtility(IIntIds, context=getSite())
    iid = intids.queryId(item, None)
    if not iid: return [] # maybe but we are not able to know
    oidsQuery = AnyOf('workflow-relevant-oids', [iid])
    pidQuery = Eq('workitem-processid', process_id)
    query = SearchQuery(oidsQuery).And(pidQuery)
    return query.searchResults()


class ContributorsIndexer(ValueIndexer):
    """ Indexer for work items with standard parameters."""

    indexName = 'workitem-contributors'

    @property
    def value(self):
        contributors = getattr(self.context, 'contributor', None)
        if contributors:
            # OK?
            return (contributors,)


@zope.component.adapter(IObjectAddedEvent, IWorkItem)
def lastActivitySubscriber(event, item):
    """Update Dublin-Core creator property"""
    dc = IZopeDublinCore(item, None)
    # Principals that can create objects do not necessarily have
    # 'zope.app.dublincore.change' permission.
    # https://bugs.launchpad.net/zope3/+bug/98124
    dc = removeSecurityProxy(dc)
    if dc is None:
        return

    # Try to find a principal for that one. If there
    # is no principal then we don't touch the list
    # of creators.
    interaction = queryInteraction()
    if interaction is not None:
        for participation in interaction.participations:
            if participation.principal is None:
                continue
            principalid = participation.principal.id
            if not principalid in dc.creators:
                dc.creators = dc.creators + (unicode(principalid), )

import zope.interface
import zope.component
from persistent import Persistent
from zope.location.location import Location
from zope.wfmc.interfaces import IWorkItem, IParticipant, ProcessError
from zope.app.component.hooks import getSite
from zope.location.interfaces import IContained
from zope.proxy import removeAllProxies

from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _


class WorkItemBase(Persistent, Location):

    zope.interface.implements(IWorkItem)
    zope.component.adapts(IParticipant)

    worklist = 'undefined'

    schema = None

    def __init__(self, participant):
        self.participant = participant

    def _appendToWorkList(self, item):
        worklist = zope.component.getUtility(
            interfaces.IWorkList,
            name=self.worklist,
            context=getSite())
        worklist.append(item)

    def _removeFromWorkList(self, item):
        worklist = zope.component.getUtility(
            interfaces.IWorkList,
            name=self.worklist,
            context=getSite())
        worklist.remove(item)
        

class ContributorWorkItem(WorkItemBase):

    worklist = 'contributor'

    schema = interfaces.IEditSchema

    def start(self):
        self._appendToWorkList(self)

    def finish(self, save):
        self.schema['save'].validate(save)
        # we remove the work item on save=='draft', too. It gets added by start again.
        self._removeFromWorkList(self)
        self.participant.activity.workItemFinished(self, save)


class EditorialReviewWorkItem(WorkItemBase):

    worklist = 'editorialreview'

    schema = interfaces.IEditorialReviewSchema

    def start(self):
        self._appendToWorkList(self)

    def finish(self, publish):
        self.schema['publish'].validate(publish)
        # we remove the work item on publish=='postpone', too. It gets
        # added by start again.
        self._removeFromWorkList(self)
        self.participant.activity.workItemFinished(self, publish)


class RemoveWorkItem(WorkItemBase):
    """ Application to remove a database item."""

    worklist = 'editorialreview'

    schema = interfaces.IRemoveSchema

    def start(self):
        obj = getattr(self.participant.activity.process.workflowRelevantData, 'object')
        # assert that object is removable, i.e. implements IRemovable
        if not interfaces.IRemovable.providedBy(obj):
            raise ProcessError(_(
                    'iremovable-not-provided',
                    u"Unremovable Object. (IRemovable interface not provided.)"
                    ))
        #TODO: add some more ways to remove the object
        if not (IContained.providedBy(obj) or 1==2):
            raise ProcessError(_(
                    'wfmc-remove-unremovable',
                    u"Unremovable Object. (Could not determine a way who to remove item.)"
                    ))
        self._appendToWorkList(self)
            
    def finish(self, remove):
        self.schema['remove'].validate(remove)

        if remove=='remove':
            obj = getattr(self.participant.activity.process.workflowRelevantData, 'object')
            # for contained item del it on container
            if IContained.providedBy(obj):
                container = obj.__parent__
                del container[obj.__name__]
            else:
                pass
        #TODO: add some more ways to remove the object

        # we remove the work item on remove=='postpone', too. It gets
        # added by start again.
        self._removeFromWorkList(self)
        self.participant.activity.workItemFinished(self, remove)


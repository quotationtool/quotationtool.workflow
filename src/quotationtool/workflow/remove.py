import zope.component
import zope.interface
from zope.wfmc.interfaces import IWorkItem, IParticipant, ProcessError
from zope.location.interfaces import IContained

from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _
from quotationtool.workflow.workitem import WorkItemBase, SimilarWorkItemsMixin


class RemoveWorkItem(WorkItemBase, SimilarWorkItemsMixin):
    """ Application to remove a database item."""

    worklist = 'editorialreview'

    oid_attributes = ('object_',) # see ISimilarWorkItems

    schema = interfaces.IRemoveSchema

    def start(self, contributor, starttime, history, object_):
        """Parameters: 
        object_: object to be removed. 
        history: the workflow history of this object."""
        self.contributor = contributor
        self.starttime = starttime
        self.object_ = object_
        self.history = history
        # assert that object is removable, i.e. implements IRemovable
        if not interfaces.IRemovable.providedBy(object_):
            raise ProcessError(_(
                    'iremovable-not-provided',
                    u"Unremovable Object. (IRemovable interface not provided.)"
                    ))
        #TODO: add some more ways to remove the object
        if not (IContained.providedBy(object_) or 1==2):
            raise ProcessError(_(
                    'wfmc-remove-unremovable',
                    u"Unremovable Object. (Could not determine a way who to remove item.)"
                    ))
        self._appendToWorkList(self)
            
    def finish(self, remove):
        self.schema['remove'].validate(remove)

        if remove=='remove':
            # assert that the item asked to be removed is not under
            # control of other workflow processes
            similars = [item for item in self.getSimilarWorkItems()]
            if similars:
                raise ProcessError(_(
                        'wfmc-remove-still-similar',
                        u"Could not remove the object. The database item is still under control of other workflow processes. These must be finished first."
                        ))

            # for contained item del it on container
            if IContained.providedBy(self.object_):
                container = self.object_.__parent__
                del container[self.object_.__name__]
            else:
                pass
        #TODO: add some more ways to remove the object

        # we remove the work item on remove=='postpone', too. It gets
        # added by start again.
        self._removeFromWorkList(self)
        self.participant.activity.workItemFinished(self, remove, self.history, self.object_)

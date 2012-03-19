"""
Workflow Pattern 29 describes a cancelling discriminator.


This module only provides base class but nothing is configured. You
may want to derive your components from it.
"""

from zope.interface import implements
import zope.component
from zope.wfmc.interfaces import ProcessError, IParticipant, IWorkItem, IProcessContext

from quotationtool.workflow import workitem
from quotationtool.workflow import interfaces


class SplitBranchWorkItem(workitem.WorkItemBase):
    
    implements(interfaces.IStandardParameters, 
               interfaces.IObjectParameter)

    contributor = starttime = message = history = object_ = None 

    def start(self, contributor, starttime, message, history, object_):
        self.contributor = contributor
        self.starttime = starttime
        self.message = message
        self.history = history
        self.object_ = object_
        self.startHook()
        self._appendToWorkList()

    def finish(self, save, message):
        self.save = save
        self.old_message = self.message
        self.message = message
        self.performer = self.worklist
        self.finishHook()
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, self.performer, self.save, self.message, self.history, self.object_)

    def destroy(self):
        """ Called by the 'reset' activity. Cancells the work item."""
        self._removeFromWorkList()

    def startHook(self):
        pass

    def finishHook(self):
        pass


class ProcessorBase(object):
    """ Base class from which the preprocessor, postprocessor and the
    postreview processor can be derived.

    Does not put any workitem on any worklist. Does nothing in fact."""

    implements(IWorkItem)
    zope.component.adapts(IParticipant)

    def __init__(self, participant):
        self.participant = participant

    def start(self, contributor, starttime, message, history, object_):
        self.contributor = contributor
        self.starttime = starttime
        self.message = message
        self.history = history
        self.object_ = object_
        self.startHook()

    def finish(self):
        self.finishHook()
        self.participant.activity.workItemFinished(self, self.message, self.history, self.object_)

    def startHook(self):
        self.finish()

    def finishHook(self):
        pass


class Preprocessor(ProcessorBase):
    """ Preprocessor application."""


class Postprocessor(ProcessorBase):
    """ Postprocessor application."""

    def OFFfinishHook(self):
        current_activity = getattr(self.participant, 'activity', None)
        process = getattr(current_activity, 'process', None)
        items = []
        #for activity_id, activity in process.activities.items():
        raise Exception(process.activities)


class PostReviewProcessor(ProcessorBase):
    """ Post review processor application."""


class Reset(object):
    """ Work item that cancells (destroys) open workitems.

    TODO: Leaves open activities untouched. Only work items are
    removed from the lists. So do we have to destroy activities, too?
    """
    
    implements(IWorkItem)
    zope.component.adapts(IParticipant)

    def __init__(self, participant):
        self.participant = participant

    def start(self, performer, history, object_):
        self.performer = performer
        self.history = history
        self.object_ = object_
        self.startHook()

    def finish(self):
        self.finishHook()
        self.participant.activity.workItemFinished(self, self.performer, self.history, self.object_)

    def startHook(self):
        self.cancelWorkItems()
        self.finish()

    def finishHook(self):
        pass

    def cancelWorkItems(self):
        current_activity = getattr(self.participant, 'activity', None)
        process = getattr(current_activity, 'process', None)
        items = []
        for activity_id, activity in process.activities.items():
            if activity == current_activity:
                continue
            # We determine the open activity by the open work
            # item. Does this have any risk?
            if activity.workitems:
                for item_id, workitem in activity.workitems.items():
                    workitem[0].destroy()
                del process.activities[activity_id]


class EditorialReview(workitem.WorkItemBase):
    """ Editorial Review work item."""

    implements(interfaces.IStandardParameters, 
               interfaces.IObjectParameter)

    contributor = starttime = message = history = object_ = None 

    def start(self, contributor, starttime, message, history, object_):
        self.contributor = contributor
        self.starttime = starttime
        self.message = message
        self.history = history
        self.object_ = object_
        self.startHook()
        self._appendToWorkList()

    def finish(self, publish, message):
        self.publish = publish
        self.old_message = self.message
        self.message = message
        self.finishHook()
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, self.publish, self.message, self.history, self.object_)

    def startHook(self):
        pass

    def finishHook(self):
        pass


class CancellingContext(object):
    
    implements(IProcessContext)

    def processFinished(self, process, history, object_):
        self.process = process
        self.history = history
        self.object_ = object_
        self.finishedHook()

    def finishedHook(self):
        pass


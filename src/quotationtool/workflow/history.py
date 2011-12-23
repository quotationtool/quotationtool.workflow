import zope.component
from zope.component import adapter, adapts
from zope.interface import implements
from zope.container.btree import BTreeContainer
from zope.container.interfaces import INameChooser
from zope.container.contained import NameChooser, Contained
import datetime
from persistent import Persistent
import zope.annotation
from zope.wfmc import process
from zope.security.management import getInteraction

from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _


class WorkflowHistory(BTreeContainer):
    """ An annotation adapter to objects that implement
    IHasWorkflowHistory."""

    implements(interfaces.IWorkflowHistory)
    adapts(interfaces.IHasWorkflowHistory)

    def append(self, notation):
        chooser = INameChooser(self)
        name = chooser.chooseName(None, None)
        self[name] = notation

    def __call__(self):
        return self.values()

    def reverse(self):
        return reverse(self.values())

WORKFLOW_HISTORY_KEY = 'quotationtool.workflow.history'

workflow_history = zope.annotation.factory(
    WorkflowHistory, WORKFLOW_HISTORY_KEY)


class NotationNameChooser(NameChooser):

    zope.interface.implements(INameChooser)
    zope.component.adapts(interfaces.IWorkflowHistory)

    def chooseName(self, name, obj):
        """ choose timestamp as name."""
        now = unicode(datetime.datetime.now())
        return super(NotationNameChooser, self).chooseName(now, obj)


class NotationBase(Persistent, Contained):
    """ Base class for notations of events, activities etc. which make
    a workflow history."""

    uids = ()

    def setUids(self):
        interaction = getInteraction()
        self.uids = [principal for principal in interaction.participations]

    @property
    def users(self):
        rc = u""
        for uid in self.uids:
            rc += uid + u", "
        if len(rc) > 2:
            return rc[:-2]
        return rc


class ProcessStartedNotation(NotationBase):

    def __init__(self, process):
        definition = getattr(process, 'definition', None)
        self.pid = getattr(definition, 'id', u'')
        self.name = getattr(definition, '__name__', u'')
        self.description = getattr(definition, 'description', u'')
        self.contributor = getattr(process.workflowRelevantData, 'contributor', u'')

    def __repr__(self):
        return _('process-started-notation',
                 u"$NAME workflow process ($ID) started by $CONTRIB. $DESC", 
                 mapping={'NAME': self.name, 'ID': self.pid,
                          'DESC': self.description, 'CONTRIB': self.contributor})

@adapter(process.ProcessStarted)
def processStartedSubscriber(event):
    try:
        history = getattr(event.process.workflowRelevantData, 'history')
        history = interfaces.IWorkflowHistory(history)
        history.append(ProcessStartedNotation(event.process))
    except Exception:
        pass


class ProcessFinishedNotation(ProcessStartedNotation):
    
    def __init__(self, process):
        definition = getattr(process, 'definition', None)
        self.pid = getattr(definition, 'id', u'')
        self.name = getattr(definition, '__name__', u'')
        self.description = getattr(definition, 'description', u'')

    def __repr__(self):
        return _('process-finished-notation',
                 u"$NAME workflow process ($ID) finished. $DESC", 
                 mapping={'NAME': self.name, 'ID': self.pid,
                          'DESC': self.description})


@adapter(process.ProcessFinished)
def processFinishedSubscriber(event):
    try:
        obj = getattr(event.process.workflowRelevantData, 'object')
        history = interfaces.IWorkflowHistory(obj)
        history.append(ProcessFinishedNotation(event.process))
    except Exception:
        pass


class ActivityStartedNotation(NotationBase):
    """ Notation of an activity started event."""

    def __init__(self, activity):
        self.id = getattr(activity, 'activity_definition_identifier', None)
        
    def __repr__(self):
        return _('activity-started-notation',
                 u"Activity $ID started.",
                 mapping={'ID': self.id})

@adapter(process.ActivityStarted)
def activityStartedSubscriber(event):
    try:
        obj = getattr(event.activity.process.workflowRelevantData, 'object')
        history = interfaces.IWorkflowHistory(obj)
        history.append(ActivityStartedNotation(event.activity))
    except Exception:
        pass


class ActivityFinishedNotation(ActivityStartedNotation):
    """ Notation of an activity finished event."""

    def __repr__(self):
        return _('activity-finished-notation',
                 u"Activity $ID finished.",
                 mapping={'ID': self.id})

@adapter(process.ActivityFinished)
def activityFinishedSubscriber(event):
    try:
        obj = getattr(event.activity.process.workflowRelevantData, 'object')
        history = interfaces.IWorkflowHistory(obj)
        history.append(ActivityFinishedNotation(event.activity))
    except Exception:
        pass


class WorkItemFinishedNotation(NotationBase):
    
    def __init__(self, application):
        self.application_id = unicode(application)

    def __repr__(self):
        return _('workitem-finished-notation',
                 u"Work item (application) '$ID' finished.",
                 mapping={'ID': self.application_id})

@adapter(process.WorkItemFinished)
def workItemFinishedSubscriber(event):
    try:
        obj = getattr(event.workitem.participant.activity.process.workflowRelevantData, 'object')
        history = interfaces.IWorkflowHistory(obj)
        history.append(WorkItemFinishedNotation(event.application))
    except Exception:
        pass


class TransitionNotation(NotationBase):
    
    def __init__(self, from_, to):
        self.from_= getattr(from_, 'activity_definition_identifier', None)
        self.to = getattr(from_, 'activity_definition_identifier', None)

    def __repr__(self):
        return _('transition-notation',
                 u"Transition from '$FROM' to '$TO'.",
                 mapping={'FROM': self.from_, 'TO': self.to})

@adapter(process.Transition)
def transitionSubscriber(event):
    try:
        if event.from_ is not None:
            obj = getattr(event.from_.process.workflowRelevantData, 'object')
        else:
            obj = getattr(event.to.process.workflowRelevantData, 'object')
        history = interfaces.IWorkflowHistory(obj)
        history.append(TransitionNotation(event.from_, event.to))
    except Exception:
        pass


class UserNotation(NotationBase):

    def __init__(self, uid, msg):
        self.uid = uid
        self.msg = msg

    def __repr__(self):
        return _('user-notation', u"$MSG (by $USER)",
                 mapping={'MSG': self.msg, 'USER': self.uid}
                 )

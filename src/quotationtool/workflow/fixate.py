from zope.interface import implements, directlyProvides, noLongerProvides
import zope.component
from zope.wfmc.interfaces import ProcessError

from quotationtool.workflow.workitem import WorkItemBase, SimilarWorkItemsMixin
from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _


class FixateWorkItem(WorkItemBase, SimilarWorkItemsMixin):
    """ Work item (application) for review activity in a
    quotationtool.fixate workflow."""

    implements(interfaces.IStandardParameters,
               interfaces.IObjectParameter)

    contributor = starttime = message = history = object_ = None 

    oid_attributes = ('object_', )

    schema = interfaces.IFixateSchema

    def start(self, contributor, starttime, message, history, object_):
        self.contributor = contributor
        self.starttime = starttime
        self.message = message
        self.history = history
        self.object_ = object_
        if not interfaces.IRemovable.providedBy(object_):
            raise ProcessError(_('fixate-iremovable-not-provided',
                                 u"Database item can't be fixated. (IRemovable not provided.)"
                                 ))
        self._appendToWorkList()

    def finish(self, fixate, message):
        self.schema['fixate'].validate(fixate)
        if fixate == 'postpone':
            message = self.message
        if fixate == 'fixate':
            if interfaces.IFixed.providedBy(self.object_):
                raise ProcessError(_('fixate-ifixed-already-provided',
                                   u"Database item is already fixed."))
            directlyProvides(self.object_, interfaces.IFixed)
        if fixate == 'unfixate':
            if not interfaces.IFixed.providedBy(self.object_):
                raise ProcessError(_('unfix-failed-not-fixed',
                                     u"Database item is not fixated. Failed to unfix it."))
            noLongerProvides(self.object_, interfaces.IFixed)
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, fixate, message, self.history, self.object_)

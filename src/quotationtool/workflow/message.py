from zope.interface import implements
import zope.component

from quotationtool.workflow.workitem import WorkItemBase, SimilarWorkItemsMixin
from quotationtool.workflow import interfaces


class MessageWorkItem(WorkItemBase, SimilarWorkItemsMixin):
    """ Work item (application) for review activity in a
    quotationtool.message workflow."""

    oid_attributes = ('object_', )

    schema = interfaces.IMessageSchema

    def start(self, contributor, starttime, message, history, object_):
        self.contributor = contributor
        self.starttime = starttime
        self.message = message
        self.history = history
        self.object_ = object_
        self._appendToWorkList()

    def finish(self, answer, message):
        self.schema['answer'].validate(answer)
        if answer == 'postpone':
            message = self.message
        self._removeFromWorkList()
        self.participant.activity.workItemFinished(self, answer, message, self.history)

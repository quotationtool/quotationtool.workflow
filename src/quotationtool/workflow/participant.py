import zope.interface
import zope.component
from zope.wfmc.interfaces import IParticipant, IActivity
from zope.app.component.hooks import getSite
from persistent import Persistent

from quotationtool.workflow.interfaces import _


class ParticipantBase(Persistent):
    
    zope.interface.implements(IParticipant)
    zope.component.adapts(IActivity)

    def __init__(self, activity):
        self.activity = activity


class ContributorParticipant(ParticipantBase):
    pass


class EditorParticipant(ParticipantBase):
    pass


class TechnicalEditorParticipant(ParticipantBase):
    pass

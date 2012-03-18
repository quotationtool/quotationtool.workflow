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
    """ Contributor participant swimming in the contributor lane."""

    __name__ = 'contributor'


class EditorParticipant(ParticipantBase):
    
    __name__ = 'editor'


class TechnicalEditorParticipant(ParticipantBase):
    
    __name__ = 'technicaleditor'


class SystemParticipant(ParticipantBase):

    __name__ = 'system'


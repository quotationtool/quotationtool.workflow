import zope.interface
import zope.schema
from zope.container.interfaces import IContainer
from zope.container.constraints import contains, containers
from zope.wfmc.interfaces import IWorkItem
from zope.i18nmessageid import MessageFactory
from zope.location.interfaces import IContained

_ = MessageFactory('quotationtool')


class IWorkFlowContainer(zope.interface.Interface):
    """ A container for all workflow relevant things."""


class IWorkList(zope.interface.Interface):
    """ A list of workflow items. 

    There are some of these lists in the workflow container, one named
    'author', one 'editorialreview', one 'technicalreview'."""

    contains(IWorkItem)

    def pop():
        """ Get the next workflow item."""

    def append(obj):
        """ Append obj to list of workflow items."""

    def remove(obj):
        """ Remove obj from list of workflow items."""


class IHistoryProcess(zope.interface.Interface):

    history = zope.interface.Attribute(""" Formal parameter in a process on an object that has a workflow history. Takes an object adaptable to IWorkflowHistory or implementing IWorkflowHistory.""")


class IEditSchema(zope.interface.Interface):

    save = zope.schema.Choice(
        title=_(u"Save"),
        description=_(u"Saving, Saving as Draft, or Move to Trash"),
        values=(_('finish'), _('draft'), _('trash')),
        required=True,
        default="finish",
        )


class IEditorialReviewSchema(zope.interface.Interface):

    publish = zope.schema.Choice(
        title=_(u"Publish"),
        description=_(u"Publish, Reject, postpone decision or return item to contributor because it needs changes."),
        values=(_('publish'), _('reject'), _('postpone'), _('needs_changes')),
        required=True,
        default="publish",
        )


class IRemovable(zope.interface.Interface):
    """ Marker interface for a database item on which a
    quotationtool.remove workflow can be processed.

    Some view components will be registered on an object implementing
    this interface."""
 

class IRemoveSchema(IHistoryProcess):
    """ Schema of workflow relevant data in a quotationtool.remove
    workflow."""

    object = zope.schema.Object(
        title=_(u"Object"),
        description=_(u"Item asked to be removed. Formal parameter passed to proc.start()."),
        schema=IRemovable,
        )

    contributor = zope.schema.TextLine(
        title=_(u"Contributor"),
        description=_(u"The user who asks the object to be removed. Formal parameter passed to proc.start()."),
        required=True,
        )

    remove = zope.schema.Choice(
        title=_(u"Remove"),
        description=_(u"Input data passed to the finish method of the application tied to editorialreview activity. Can ether be Remove or Reject or Postpone decision."),
        values=('remove', 'reject', 'postpone'),
        required=True,
        default="remove",
        )


### Workflow History

class IHasWorkflowHistory(zope.interface.Interface):
    """ A marker interface for a object that has a workflow
    history. It will be adaptable to an annotation
    IWorkflowHistory."""


class IWorkflowHistory(zope.interface.Interface):
    """ A database item's workflow history, i.e. notation of
    activities on it and events."""

    def append(notation):
        """ Append a notation of an activity or event to the
        history."""

    def __call__():
        """ Return the full history."""

    def reverse():
        """ Return the full history in reverse order."""


class INotation(zope.interface.Interface):
    """ A notation of an activity or event which will be part of the
    items workflow history."""

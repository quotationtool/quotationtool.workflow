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


class ISimilarWorkItems(zope.interface.Interface):
    """ There would be system errors if a database item was
    removed by one workflow process but was still under control of
    another workflow process. So we need some tool to be aware of the
    database items a work item/a workflow process deals with. 

    This is done by indexing the intids of the database items relevant
    for a work item. There is an indexer registered for workitems that
    implement ISimilarWorkItems and that gets the intids by means of
    'oid_attributes'.

    Similar work items (== items that work on the same database items)
    can the be found by calling getSimilarWorkItems(). This method
    simply queries the index."""

    oid_attributes = zope.schema.Tuple(
        title=_(u"Object Id Attributes"),
        description=_(u"Names of attributes that hold database items relevant for the workflow process which are/may be registered by an IntIds utility."),
        required=True,
        default=(),
        )

    def getSimilarWorkItems():
        """ Returns an iterator over similar work items, i.e. work items that """


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


class IWorkflowInfo(zope.interface.Interface):

    process_name = zope.schema.TextLine(
        title=u"Process Name",
        description=u"Name of the workflow process the item is part of.",
        readonly=True,
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


class IWorkItemForm(zope.interface.Interface):
    """ A form for managing work items"""

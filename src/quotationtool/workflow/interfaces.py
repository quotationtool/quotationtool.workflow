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


class IStandardParameters(zope.interface.Interface):
    """ Work items may be standardized. It makes sense to pass some
    formal parameters to their start method."""

    contributor = zope.schema.TextLine(
        title=_(u"Contributor"),
        description=_(u"The user who asks the object to be removed."),
        required=False,
        )

    starttime = zope.schema.Datetime(
        title=_(u"Start Time"),
        description=_(u"Timestamp when the process was started."),
        required=False,
        )

    message = zope.schema.Text(
        title=_(u"Message"),
        description=_(u"Message of the contributor to the editorial staff."),
        required=False,
        )

    history = zope.schema.Object(
        title=_(u"History"),
        description=_(u"The workflow history where the notations should go. This is expected to be an IN or INOUT parameter."),
        required=False,
        schema=IWorkflowHistory,
        )


class IObjectParameter(zope.interface.Interface):
    """ A workflow item which takes a database item as formal
    parameter. IN or INOUT parameter."""

    object_ = zope.interface.Attribute(""" Database item under workflow controle""")


class IWorkflowInfo(zope.interface.Interface):
    """ Get some information about the workflow process. This is
    implemented by an adapter to work items."""

    process_name = zope.schema.TextLine(
        title=u"Process Name",
        description=u"Name of the workflow process the item is part of.",
        readonly=True,
        )


class IWorkItemForm(zope.interface.Interface):
    """ A form for managing work items."""


class IEditSchema(zope.interface.Interface):
    """ """

    save = zope.schema.Choice(
        title=_(u"Save"),
        description=_(u"Saving, Saving as Draft, or Move to Trash"),
        values=('finish', 'draft', 'trash'),
        required=True,
        default="finish",
        )


class IEditorialReviewSchema(zope.interface.Interface):

    publish = zope.schema.Choice(
        title=_(u"Publish"),
        description=_(u"Publish, Reject, postpone decision or return item to contributor because it needs changes."),
        values=('publish', 'reject', 'postpone', 'needs_changes'),
        required=True,
        default="publish",
        )


class IRemovable(zope.interface.Interface):
    """ Marker interface for a database item on which a
    quotationtool.remove workflow can be processed.
    
    Some view components will be registered on an object implementing
    this interface."""


class IFixed(zope.interface.Interface):
    """ Marker interface for a database item which can't be
    removed."""


class IRemoveSchema(zope.interface.Interface):
    """ Schema of workflow relevant data in a quotationtool.remove
    workflow."""

    remove = zope.schema.Choice(
        title=_(u"Remove"),
        description=_(u"Input data passed to the finish method of the application tied to editorialreview activity. Can ether be Remove or Reject or Postpone decision."),
        values=('remove', 'reject', 'postpone'),
        required=True,
        default="remove",
        )


class ISubjectOfMessage(zope.interface.Interface):
    """ Marker interface for a content object on which a
    quotationtool.message workflow can be performed."""


class IMessageSchema(zope.interface.Interface):

    answer = zope.schema.Choice(
        title=u"Answer",
        description=u"Input data passed to the finish method of the application.",
        values=('answer', 'postpone'),
        required=True,
        default='answer',
        )


class IFixateSchema(zope.interface.Interface):
    
    fixate = zope.schema.Choice(
        title=u"Fixate",
        description=u"Input data passed to the finish method of the application.",
        values=('fixate', 'unfixate', 'reject', 'postpone'),
        required=True,
        default='fixate',
        )

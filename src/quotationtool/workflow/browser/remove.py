import datetime
import zope.component
from zope.interface import implements
from z3c.form import field, button
from z3c.formui import form
from zope.wfmc.interfaces import IProcessDefinition
from zope.traversing.browser import absoluteURL
from z3c.pagelet.browser import BrowserPagelet
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView
from z3c.ptcompat import ViewPageTemplateFile

from quotationtool.skin.interfaces import ITabbedContentLayout

from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _
from quotationtool.workflow.history import UserNotation


comment = zope.schema.Text(
    title=_('remove-comment-title',
            u"Message"),
    description=_('remove-comment-desc',
                  u"Why you want the item to be deleted? Please provide a short message to the editorial staff."),
    required=True,
    )
comment.__name__ = 'workflow-message'

review_comment = zope.schema.Text(
    title=_('removereview-comment-title',
            u"Comment"),
    description=_('removereview-comment-desc',
                  u"Please give a short comment on your decision, especially if you reject the remove request."),
    required=False,
    )
review_comment.__name__ = 'workflow-message'

class RemoveRequestForm(form.Form):

    implements(ITabbedContentLayout)

    label = _('removerequestform-label',
              u"Remove database item")

    process_id = 'quotationtool.remove'

    fields = field.Fields(comment)

    ignoreContext = True
    ignoreReadonly = True

    @button.buttonAndHandler(_(u"Remove"), name='remove')
    def handleRemove(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        history = interfaces.IWorkflowHistory(self.context)
        principal = getattr(self.request, 'principal', None)
        pd = zope.component.getUtility(
            IProcessDefinition, name=self.process_id, 
            context=self.context)
        proc = pd()
        # TODO: Note that we have to remove the security proxy!
        proc.start(getattr(principal, 'id', u"Unkown"),
                   datetime.datetime.now(),
                   removeAllProxies(history),
                   removeAllProxies(self.context) 
                   )
        history.append(UserNotation(
                getattr(principal, 'id', u"Unknown"),
                data['workflow-message']
                ))
        #self.template = ViewPageTemplateFile('remove_process_started.pt')
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.context, self.request)

    def nextURL(self):
        return absoluteURL(self.context, self.request) + u"/@@removeProcessStarted.html"


class RemoveProcessStarted(BrowserPagelet):
    """ Notification that the removal process started."""

    implements(ITabbedContentLayout)


class RemoveWorkItemLabel(BrowserView):
    """ Label for work item."""

    def __call__(self):
        return _('remove-workitem-label',
                 u"Remove")

class RemoveEditorialReview(form.Form):
    
    implements(interfaces.IWorkItemForm)

    fields = field.Fields(review_comment)

    label = _('removeeditorialreview-label', u"Editorial Review on Remove Request")

    info = _('removeeditorialreview-info', u"You can either accept the request, reject it or postpone your decision.")

    ignoreContext = True
    ignoreReadonly = True

    def _handle(self, remove):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        history = self.context.history
        principal = getattr(self.request, 'principal', None)
        history.append(UserNotation(
                getattr(principal, 'id', u"Unkown"),
                data['workflow-message']))
        #get next URL before removing work item
        url = self.nextURL()
        self.context.finish(remove)
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"Remove"), name="remove")
    def handleRemove(self, action):
        self._handle('remove')
        
    @button.buttonAndHandler(_(u"Reject"), name="reject")
    def handleReject(self, action):
        self._handle('reject')
        
    @button.buttonAndHandler(_(u"Postpone"), name="postpone")
    def handlePostpone(self, action):
        self._handle('postpone')

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return absoluteURL(self.context.__parent__, self.request)

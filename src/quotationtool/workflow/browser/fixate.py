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
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile as ViewletPageTemplateFile
from zope.viewlet.viewlet import ViewletBase
from cgi import escape

from quotationtool.skin.interfaces import ITabbedContentLayout

from quotationtool.workflow import interfaces
from quotationtool.workflow.interfaces import _
from quotationtool.workflow.history import UserNotation
from quotationtool.workflow.browser import common

message = zope.schema.Text(
    title=_('fixate-message-title',
            u"Message"),
    description=_('fixate-message-desc',
                  u"Please enter the message you want to send to the editorial staff."),
    required=True,
    )
message.__name__ = 'workflow-message'

answer = zope.schema.Text(
    title=_('fixate-comment-title',
            u"Comment"),
    description=_('fixate-comment-desc',
                  u"Please give a (short) comment about the request, especially if you reject it."),
    required=False,
    )
answer.__name__ = 'workflow-message'

class FixateRequestForm(form.Form):

    implements(ITabbedContentLayout)

    label = _('fixaterequestform-label',
              u"Fixation of Database Item")

    info = _('fixaterequestform-info',
             u"Using the form below you can ask the editorial staff to protect this database item against removal (or remove a protection). The site's editors will read your message and decide what to do.")

    process_id = 'quotationtool.fixate'

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.getURL() + u"#tabs"

    fields = field.Fields(message)

    ignoreContext = True
    ignoreReadonly = True

    @button.buttonAndHandler(_(u"Submit"), name='fixate')
    def handleFixate(self, action):
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
                   data['workflow-message'],
                   removeAllProxies(history),
                   removeAllProxies(self.context) 
                   )
        history.append(UserNotation(
                getattr(principal, 'id', u"Unknown"),
                data['workflow-message']
                ))
        #self.template = ViewPageTemplateFile('fixate_process_started.pt')
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        url = absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

    def nextURL(self):
        return absoluteURL(self.context, self.request) + u"/@@fixateProcessStarted.html#tabs"


class FixateProcessStarted(BrowserPagelet):
    """ Notification that the fixate process started."""

    implements(ITabbedContentLayout)


class FixateEditorialReview(form.Form):
    """ Form for the the work item."""
    
    implements(interfaces.IWorkItemForm)

    fields = field.Fields(answer)

    label = _('fixateeditorialreview-label', u"Editorial Review of Fixation Request")

    info = _('fixateeditorialreview-info', u"Please decide to fixate/unfixate the database item.")

    ignoreContext = True
    ignoreReadonly = True

    def _handle(self, fixate):
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
        self.context.finish(fixate, data['workflow-message'])
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"Fixate"), name="fixate")
    def handleFixate(self, action):
        self._handle('fixate')
        
    @button.buttonAndHandler(_(u"Unfixate"), name="unfixate")
    def handleUnfixate(self, action):
        self._handle('unfixate')
        
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

    def contributor(self):
        return common.getPrincipalTitle(self.context.contributor)

    def message(self):
        return escape(self.context.message).replace('\n', '<br />')


class FixateItemAction(ViewletBase):
    
    template = ViewletPageTemplateFile('fixate_action.pt')

    def render(self):
        return self.template()


class FixedFlag(ViewletBase):
    
    template = ViewletPageTemplateFile('fixed.pt')

    def render(self):
        if interfaces.IFixed.providedBy(self.context):
            return self.template()
        return u""

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
    title=_('message-message-title',
            u"Message"),
    description=_('message-message-desc',
                  u"Please enter the message you want to send to the editorial staff."),
    required=True,
    )
message.__name__ = 'workflow-message'

answer = zope.schema.Text(
    title=_('message-answer-title',
            u"Answer"),
    description=_('message-answer-desc',
                  u"Please give a (short) answer to the message."),
    required=True,
    )
answer.__name__ = 'workflow-message'

class MessageRequestForm(form.Form):

    implements(ITabbedContentLayout)

    label = _('messagerequestform-label',
              u"Message about database item")

    info = _('messagerequestform-info',
             u"Using the form below you can send a message to the editorial staff. It should be about this database item. May be you found a typo or an other mistake, want changes to be made. The site's editors will read your message and decide what to do. You can read their answer by visiting the tab called 'Workflow' under this database item.")

    process_id = 'quotationtool.message'

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.getURL() + u"#tabs"

    fields = field.Fields(message)

    ignoreContext = True
    ignoreReadonly = True

    @button.buttonAndHandler(_(u"Send"), name='send')
    def handleSend(self, action):
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
        #self.template = ViewPageTemplateFile('message_process_started.pt')
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"Cancel"), name="cancel")
    def handleCancel(self, action):
        url = absoluteURL(self.context, self.request)
        self.request.response.redirect(url)

    def nextURL(self):
        return absoluteURL(self.context, self.request) + u"/@@messageProcessStarted.html#tabs"


class MessageProcessStarted(BrowserPagelet):
    """ Notification that the message process started."""

    implements(ITabbedContentLayout)


class MessageWorkItemLabel(BrowserView):
    """ Label for work item."""

    def __call__(self):
        return _('message-workitem-label',
                 u"Message")

class MessageEditorialReview(form.Form):
    
    implements(interfaces.IWorkItemForm)

    fields = field.Fields(answer)

    label = _('messageeditorialreview-label', u"Editorial Review of Message")

    info = _('messageeditorialreview-info', u"Please write an answer to the user's message about the item.")

    ignoreContext = True
    ignoreReadonly = True

    def _handle(self, answr):
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
        self.context.finish(answr, data['workflow-message'])
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u"Answer"), name="answer")
    def handleAnswer(self, action):
        self._handle('answer')
        
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


class MessageItemAction(ViewletBase):
    
    template = ViewletPageTemplateFile('message_action.pt')

    def render(self):
        return self.template()

from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class WorkItemLabel(BrowserView):
    """ General label for work items"""
    
    template = ViewPageTemplateFile('workitem_label.pt')

    def __call__(self):
        return self.template()

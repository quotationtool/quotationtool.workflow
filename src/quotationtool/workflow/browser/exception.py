from zope.publisher.browser import BrowserView
from z3c.pagelet.browser import BrowserPagelet

from quotationtool.workflow.interfaces import _


class ProcessErrorLabel(BrowserView):
    """ A label view for a process error."""

    def __call__(self):
        return _('workflow-process-error-label',
                 u"Error in Workflow Process")


class ProcessErrorPagelet(BrowserPagelet):
    """ A pagelet for process errors."""

import zope.component
from zope.dublincore.interfaces import IWriteZopeDublinCore
from z3c.indexer.index import SetIndex
from z3c.indexer.interfaces import IIndex

from quotationtool.site.interfaces import INewQuotationtoolSiteEvent

from quotationtool.workflow.container import WorkFlowContainer
from quotationtool.workflow.worklist import WorkList
from quotationtool.workflow import interfaces


@zope.component.adapter(INewQuotationtoolSiteEvent)
def createWorkFlowContainer(event):
    site = event.object
    sm = site.getSiteManager()

    site['workflow'] = container = WorkFlowContainer()

    container['contributor'] = contributor = WorkList()
    sm.registerUtility(contributor, interfaces.IWorkList, name='contributor')
    dc = IWriteZopeDublinCore(contributor)
    dc.title = u"Contribution"
    dc.description = u"List of work items to be worked on by contributors."

    container['editor'] = editor = WorkList()
    sm.registerUtility(editor, interfaces.IWorkList, name='editor')
    dc = IWriteZopeDublinCore(editor)
    dc.title = u"Editorial Review"
    dc.description = u"List of work items to be reviewed by the site's editors."

    container['technicaleditor'] = technicaleditor = WorkList()
    sm.registerUtility(technicaleditor, interfaces.IWorkList, name='technicaleditor')
    dc = IWriteZopeDublinCore(technicaleditor)
    dc.title = u"Technical Review"
    dc.description = u"List of work items to be reviewed by the site's technical staff."

    container['script'] = script = WorkList()
    sm.registerUtility(script, interfaces.IWorkList, name='script')
    dc = IWriteZopeDublinCore(script)
    dc.title = u"Script"
    dc.description = u"List of work items generated by automatic scripts, e.g. database evolutions. Scripts usually create a huge bunch of items."

    sm['default']['workflow-relevant-oids'] = oids = SetIndex()
    sm.registerUtility(oids, IIndex, name='workflow-relevant-oids')

    sm['default']['workitem-contributor'] = contribs = SetIndex()
    sm.registerUtility(contribs, IIndex, name='workitem-contributors')

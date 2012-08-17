import unittest
import doctest
import os
import zope.component
from zope.component.testing import setUp, tearDown, PlacelessSetup
from zope.app.testing import placelesssetup
from zope.site.testing import siteSetUp
from zope.configuration import xmlconfig
from zope.site.folder import rootFolder
from zope.app.testing.setup import placefulSetUp, placefulTearDown

import quotationtool.workflow
from quotationtool.workflow import testing

_flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS


def setUpZCML(test):
    setUp(test)
    xmlconfig.XMLConfig('configure.zcml', quotationtool.workflow)()

def zcml(s):
    context = xmlconfig.file('meta.zcml', package=zope.app.wfmc)
    xmlconfig.string(s, context)

def setUpOIDs(test):
    """ Test setup with intids utility and setindex for object ids of
    workflow relevant database items."""
    setUpZCML(test)
    from testing import DummyIntIds
    from zope.intid.interfaces import IIntIds
    if zope.component.queryUtility(IIntIds):
        raise Exception
    intids = DummyIntIds()
    zope.component.provideUtility(intids, IIntIds)
    testing.setUpIndices(test)
    from testing import addIntIdSubscriber, removeIntIdSubscriber
    zope.component.provideHandler(addIntIdSubscriber)
    zope.component.provideHandler(removeIntIdSubscriber)

def setUpDemo(test):
    placelesssetup.setUp(test)
    test.globs['this_directory'] = os.path.dirname(__file__)
    xmlconfig.XMLConfig('configure.zcml', quotationtool.workflow)()


class SiteCreationTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SiteCreationTests, self).setUp()
        setUpZCML(self)
        self.root_folder = rootFolder()

    def tearDown(self):
        placefulTearDown()
        tearDown(self)

    def test_WorkFlowContainer(self):
        from quotationtool.site.site import QuotationtoolSite
        self.root_folder['quotationtool'] = site = QuotationtoolSite()
        from quotationtool.workflow.container import WorkFlowContainer
        self.assertTrue(isinstance(site['workflow'], WorkFlowContainer))
        from quotationtool.workflow.worklist import WorkList
        self.assertTrue(isinstance(site['workflow']['contributor'], WorkList))
        self.assertTrue(isinstance(site['workflow']['editor'], WorkList))
        self.assertTrue(isinstance(site['workflow']['technicaleditor'], WorkList))
        self.assertTrue(isinstance(site['workflow']['script'], WorkList))

    def test_Indices(self):
        from z3c.indexer.interfaces import IIndex
        from quotationtool.site.site import QuotationtoolSite
        self.root_folder['quotationtool'] = site = QuotationtoolSite()
        oids = zope.component.queryUtility(IIndex, name='workflow-relevant-oids', context=site)
        self.assertTrue(oids is not None)
        self.assertTrue(oids is site.getSiteManager()['default']['workflow-relevant-oids'])

def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(SiteCreationTests),
            doctest.DocFileSuite('demo.txt', globs={'zcml': zcml},
                                 setUp = setUpDemo,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('remove.txt',
                                 setUp = setUpOIDs,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('fixate.txt',
                                 setUp = setUpOIDs,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('history.txt',
                                 setUp = setUpOIDs,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('message.txt',
                                 setUp = setUpOIDs,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            ))

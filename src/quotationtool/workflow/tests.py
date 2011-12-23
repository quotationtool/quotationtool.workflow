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

_flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS


def setUpZCML(test):
    setUp(test)
    xmlconfig.XMLConfig('configure.zcml', quotationtool.workflow)()

def zcml(s):
    context = xmlconfig.file('meta.zcml', package=zope.app.wfmc)
    xmlconfig.string(s, context)

def setUpArticle(test):
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
        self.assertTrue(isinstance(site['workflow']['editorialreview'], WorkList))
        self.assertTrue(isinstance(site['workflow']['technicalreview'], WorkList))
        self.assertTrue(isinstance(site['workflow']['script'], WorkList))


def test_suite():
    return unittest.TestSuite((
            unittest.makeSuite(SiteCreationTests),
            doctest.DocFileSuite('article.txt', globs={'zcml': zcml},
                                 setUp = setUpArticle,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('remove.txt',
                                 setUp = setUpZCML,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            doctest.DocFileSuite('history.txt',
                                 setUp = setUpZCML,
                                 tearDown = tearDown,
                                 optionflags=_flags),
            ))

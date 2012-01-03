import unittest
import doctest
from zope.component.testing import setUp, tearDown, PlacelessSetup
import zope.interface
import zope.component
from zope.configuration.xmlconfig import XMLConfig, xmlconfig
import zope.publisher.browser
import z3c.form.interfaces
import z3c.layer
from zope.security.testing import Principal
from zope.intid.interfaces import IIntIds
from zope.site.folder import rootFolder

import quotationtool.workflow

from quotationtool.skin.interfaces import IQuotationtoolBrowserLayer 


def setUpZCML(test):
    """
        >>> XMLConfig('configure.zcml', quotationtool.workflow)()
        >>> XMLConfig('configure.zcml', quotationtool.workflow.browser)()

    """
    setUp(test)
    XMLConfig('configure.zcml', quotationtool.workflow)()
    XMLConfig('configure.zcml', quotationtool.workflow.browser)()


def setUpWorkLists(site):
    from quotationtool.workflow.container import WorkFlowContainer
    site['workflow'] = container = WorkFlowContainer()
    from quotationtool.workflow.worklist import WorkList
    from quotationtool.workflow.interfaces import IWorkList
    for name in ('contributor', 'editor', 'technicaleditor', 'script'):
        container[name] = WorkList()
        zope.component.provideUtility(container[name], IWorkList, name=name)


from zope.interface import Interface, implements
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from zope.container.contained import Contained
from zope.annotation.interfaces import IAttributeAnnotatable
from persistent import Persistent
from quotationtool.workflow.interfaces import IHasWorkflowHistory, IRemovable

class IFoo(Interface):
    pass

class Foo(Contained, Persistent):
    implements(IFoo, IHasWorkflowHistory, IRemovable, IAttributeAnnotatable)

class IBar(Interface):
    ref = zope.schema.Object(title=u"Reference", schema=IFoo)

class Bar(Contained, Persistent):
    implements(IBar, IHasWorkflowHistory, IRemovable, IAttributeAnnotatable)
    ref = FieldProperty(IBar['ref'])

def getRef(obj, catalog):
    return getattr(obj, 'ref', None)

def generateContent(container):
    from zope.container.sample import SampleContainer
    #container = SampleContainer()
    container['foo1'] = foo1 = Foo()
    container['foo2'] = Foo()
    container['foo3'] = Foo()
    container['foo4'] = Foo()
    container['bar1'] = bar1 = Bar()
    container['bar2'] = bar2 = Bar()
    bar1.ref = foo1
    bar2.ref = foo1
    return container

def generateSite(root):
    from quotationtool.site.site import QuotationtoolSite
    root['quotationtool'] = site = QuotationtoolSite()
    return site

def setUpRelationCatalog(test):
    import zc.relation
    from quotationtool.workflow.testing import dump, load
    cat = zc.relation.catalog.Catalog(dump, load)
    zope.component.provideUtility(cat, zc.relation.interfaces.ICatalog)
    cat.addValueIndex(IBar['ref'], dump=dump, load=load, name='ibar-ref')

def setUpIntIds(test):
    from quotationtool.workflow.testing import DummyIntIds
    from quotationtool.workflow.testing import removeIntIdSubscriber, addIntIdSubscriber
    intids = DummyIntIds()
    zope.component.provideUtility(intids, IIntIds)
    zope.component.provideHandler(removeIntIdSubscriber)
    zope.component.provideHandler(addIntIdSubscriber)

def setUpIndexes(test):
    from z3c.indexer.index import SetIndex
    from z3c.indexer.interfaces import IIndex
    idx = SetIndex()
    zope.component.provideUtility(idx, IIndex, name='workflow-relevant-oids')

def startRemove(contributor, obj):
    from quotationtool.workflow.interfaces import IWorkflowHistory
    history = IWorkflowHistory(obj)
    import datetime
    from zope.wfmc.interfaces import IProcessDefinition
    pd = zope.component.getUtility(IProcessDefinition, 'quotationtool.remove')
    proc = pd()
    proc.start(contributor, datetime.datetime.now(), history, obj)

class SkinTests(PlacelessSetup, unittest.TestCase):
    
    def testLayer(self):
        pass


class TestRequest(zope.publisher.browser.TestRequest):
    # we have to implement the layer interface which the templates and
    # layout are registered for. See the skin.txt file in the
    # zope.publisher.browser module.
    zope.interface.implements(
        z3c.form.interfaces.IFormLayer,
        IQuotationtoolBrowserLayer)

    principal = Principal('testing')



class RemoveTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(RemoveTests, self).setUp()
        setUpZCML(self)
        setUpIntIds(self)
        setUpRelationCatalog(self)
        self.root = rootFolder()
        setUpWorkLists(self.root)
        setUpIndexes(self)
        generateContent(self.root)
        from quotationtool.workflow.interfaces import IWorkList
        self.worklist = zope.component.getUtility(IWorkList, name='editor', context=self.root)

    def tearDown(self):
        tearDown(self)

    def test_RemoveProcessStarted(self):
        from quotationtool.workflow.browser import remove
        pagelet = remove.RemoveProcessStarted(self.root['foo2'], TestRequest())
        self.assertTrue(isinstance(pagelet.render(), unicode))

    def test_RemoveRequestForm(self):
        from quotationtool.workflow.browser import remove
        pagelet = remove.RemoveRequestForm(self.root['foo2'], TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.render(), unicode))

        request = TestRequest(form={
                'form.widgets.workflow-message': u"Please delete it.",
                'form.buttons.remove': u"Remove",
                })
        pagelet = remove.RemoveRequestForm(self.root['foo2'], request)
        pagelet.update()
        self.assertTrue(len(self.worklist) == 1)

    def test_RemoveEditorialReview(self):
        from quotationtool.workflow.browser import remove
        startRemove(TestRequest().principal.id, self.root['foo2'])
        item = self.worklist.pop()
        pagelet = remove.RemoveEditorialReview(item, TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.render(), unicode))

    def test_Reject(self):
        from quotationtool.workflow.browser import remove
        startRemove(TestRequest().principal.id, self.root['foo2'])
        item = self.worklist.pop()
        request = TestRequest(form={
                'form.widgets.workflow-message': u"?",
                'form.buttons.reject': u"reject",
                })
        pagelet = remove.RemoveEditorialReview(item, request)
        pagelet.update()
        self.assertTrue(len(self.worklist) == 0)
        self.assertTrue('foo2' in self.root)

    def test_Postpone(self):
        from quotationtool.workflow.browser import remove
        startRemove(TestRequest().principal.id, self.root['foo2'])
        item = self.worklist.pop()
        request = TestRequest(form={
                'form.widgets.workflow-message': u"?",
                'form.buttons.postpone': u"Postpone",
                })
        pagelet = remove.RemoveEditorialReview(item, request)
        pagelet.update()
        self.assertTrue(len(self.worklist) == 1)
        self.assertTrue('foo2' in self.root)

    def test_Remove(self):
        from quotationtool.workflow.browser import remove
        startRemove(TestRequest().principal.id, self.root['foo2'])
        item = self.worklist.pop()
        request = TestRequest(form={
                'form.widgets.workflow-message': u"Yes!",
                'form.buttons.remove': u"Remove",
                })
        pagelet = remove.RemoveEditorialReview(item, request)
        pagelet.update()
        self.assertTrue(len(self.worklist) == 0)
        self.assertTrue(not 'foo2' in self.root)

    def test_StillRelations(self):
        from quotationtool.workflow.browser import remove
        from zc.relation.interfaces import ICatalog
        cat = zope.component.getUtility(ICatalog, context=self.root)
        cat.index(self.root['foo1'])
        cat.index(self.root['bar1'])
        cat.index(self.root['bar2'])
        startRemove(TestRequest().principal.id, self.root['foo1'])
        item = self.worklist.pop()
        request = TestRequest(form={
                'form.widgets.workflow-message': u"Yes!",
                'form.buttons.remove': u"Remove",
                })
        pagelet = remove.RemoveEditorialReview(item, request)
        from zope.wfmc.interfaces import ProcessError
        self.assertRaises(ProcessError, pagelet.update)
        self.assertTrue(len(self.worklist) == 1)
        self.assertTrue('foo1' in self.root)
        
    def test_StillSimilarWorkItems(self):
        from quotationtool.workflow.browser import remove
        startRemove(TestRequest().principal.id, self.root['foo2'])
        startRemove(TestRequest().principal.id, self.root['foo2'])
        item = self.worklist.pop()
        request = TestRequest(form={
                'form.widgets.workflow-message': u"Yes!",
                'form.buttons.remove': u"Remove",
                })
        pagelet = remove.RemoveEditorialReview(item, request)
        from zope.wfmc.interfaces import ProcessError
        self.assertRaises(ProcessError, pagelet.update)
        self.assertTrue(len(self.worklist) == 2)
        self.assertTrue('foo2' in self.root)
        
    def test_ItemInWorkList(self):
        from quotationtool.workflow.browser import worklist
        startRemove(TestRequest().principal.id, self.root['foo2'])
        pagelet = worklist.WorkListTable(self.worklist, TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.render(), unicode))
        
    def test_ItemInSimilarWorkItemsTable(self):
        from quotationtool.workflow.browser import worklist
        startRemove(TestRequest().principal.id, self.root['foo2'])
        startRemove(TestRequest().principal.id, self.root['foo2'])
        item = self.worklist.pop()
        view = worklist.SimilarWorkItemsTable(item, TestRequest())
        self.assertTrue(isinstance(view(), unicode))


class ListWorkListsTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(ListWorkListsTests, self).setUp()
        setUpZCML(self)
        self.root = rootFolder()
        setUpWorkLists(self.root)

    def tearDown(self):
        tearDown(self)

    def test_ListWorkLists(self):
        from quotationtool.workflow.browser import worklist
        pagelet = worklist.ListWorkLists(self.root['workflow'], TestRequest())
        pagelet.update()
        self.assertTrue(isinstance(pagelet.render(), unicode))


def test_suite():
    return unittest.TestSuite((
            doctest.DocTestSuite(setUp = setUp, tearDown = tearDown),
            unittest.makeSuite(RemoveTests),
            unittest.makeSuite(ListWorkListsTests),
            ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')

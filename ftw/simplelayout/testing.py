from collective import dexteritytextindexer
from ftw.builder import registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.tests import builders
from ftw.testing.layer import ComponentRegistryLayer
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.dexterity.fti import DexterityFTI
from plone.supermodel import model
from plone.testing import z2
from plone.testing import zca
from unittest2 import TestCase
from zope import schema
from zope.component import provideAdapter
from zope.configuration import xmlconfig
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView


class SimplelayoutZCMLLayer(ComponentRegistryLayer):

    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def setUp(self):
        super(SimplelayoutZCMLLayer, self).setUp()

        import ftw.simplelayout.tests
        self.load_zcml_file('tests.zcml', ftw.simplelayout.tests)

SIMPLELAYOUT_ZCML_LAYER = SimplelayoutZCMLLayer()


class FtwSimplelayoutLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.simplelayout
        xmlconfig.file('configure.zcml', ftw.simplelayout,
                       context=configurationContext)
        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.simplelayout:lib')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        login(portal, TEST_USER_NAME)


class FtwSimplelayoutContentLayer(FtwSimplelayoutLayer):
    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.simplelayout:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        login(portal, TEST_USER_NAME)


class ISampleDXBlockSchema(model.Schema):
    title = schema.TextLine(
        title=u'Title',
        required=False)
    dexteritytextindexer.searchable('text')
    text = RichText(
        title=u'Text',
        required=False,
        allowed_mime_types=('text/html',))

alsoProvides(ISampleDXBlockSchema, IFormFieldProvider)


class ISampleDXBlock(Interface):
    pass


class SampleBlock(Item):
    implements(ISampleDXBlock)


class ISampleSimplelayoutContainerSchema(model.Schema):
    pass


class ISampleSimplelayoutContainer(Interface):
    pass


class SampleContainer(Container):
    implements(ISampleSimplelayoutContainer)


class SampleContainerBuilder(DexterityBuilder):
    portal_type = 'SampleContainer'


class SampleBlockBuilder(DexterityBuilder):
    portal_type = 'SampleBlock'


registry.builder_registry.register('sample block', SampleBlockBuilder)
registry.builder_registry.register('sample container', SampleContainerBuilder)


class SimplelayoutTestCase(TestCase):

    def assert_recursive_persistence(self, structure):

        def is_persistent(item):
            if not isinstance(item, basestring) and not isinstance(item, int):
                assert isinstance(item, PersistentMapping) or \
                    isinstance(item, PersistentList), \
                    '{0} needs to be persistent'.format(str(item))

                if hasattr(item, 'values'):
                    item = item.values()
                for subitem in item:
                    is_persistent(subitem)
            else:
                return

        is_persistent(structure)

    def setup_sample_ftis(self,
                          portal):

        types_tool = portal.portal_types

        # Simplelayout Container
        self.fti = DexterityFTI('SampleContainer')
        self.fti.schema = 'ftw.simplelayout.testsing.ISampleSimplelayoutContainerSchema'
        self.fti.klass = 'ftw.simplelayout.testing.SampleContainer'
        self.fti.behaviors = (
            'ftw.simplelayout.interfaces.ISimplelayout',
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'plone.app.content.interfaces.INameFromTitle',
            'collective.dexteritytextindexer.behavior.IDexterityTextIndexer')
        self.fti.default_view = '@@simplelayout-view'
        types_tool._setObject('SampleContainer', self.fti)

        # Simplelayout Block
        self.fti = DexterityFTI('SampleBlock')
        self.fti.schema = 'ftw.simplelayout.testing.ISampleDXBlockSchema'
        self.fti.klass = 'ftw.simplelayout.testing.SampleBlock'
        self.fti.default_view = 'block_view'
        self.fti.behaviors = (
            'ftw.simplelayout.interfaces.ISimplelayoutBlock',
            'plone.app.lockingbehavior.behaviors.ILocking',
            'plone.app.content.interfaces.INameFromTitle',)

        types_tool._setObject('SampleBlock', self.fti)

        contentpage_fti = types_tool.get('SampleContainer')
        contentpage_fti.allowed_content_types = (
            'SampleBlock', )

    def setup_block_views(self):

        class SampleBlockView(BaseBlock):

            def __call__(self):
                return 'OK'

        provideAdapter(SampleBlockView,
                       adapts=(ISampleDXBlock, Interface),
                       provides=IBrowserView,
                       name='block_view')

        class SampleBlockViewDifferent(BaseBlock):

            def __call__(self):
                return 'OK - different view'

        provideAdapter(SampleBlockViewDifferent,
                       adapts=(ISampleDXBlock, Interface),
                       provides=IBrowserView,
                       name='block_view_different')

        class SampleBlockViewBroken(BaseBlock):

            def __call__(self):
                raise

        provideAdapter(SampleBlockViewBroken,
                       adapts=(ISampleDXBlock, Interface),
                       provides=IBrowserView,
                       name='block_view_broken')


FTW_SIMPLELAYOUT_FIXTURE = FtwSimplelayoutLayer()
FTW_SIMPLELAYOUT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_SIMPLELAYOUT_FIXTURE,), name="FtwSimplelayout:Integration")
FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_SIMPLELAYOUT_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name='FtwSimplelayout:Functional')

FTW_SIMPLELAYOUT_CONTENT_FIXTURE = FtwSimplelayoutContentLayer()
FTW_SIMPLELAYOUT_CONTENT_TESTING = FunctionalTesting(
    bases=(FTW_SIMPLELAYOUT_CONTENT_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name='FtwSimplelayoutContent:Functional')

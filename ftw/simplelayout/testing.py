from ftw.builder import registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.properties import MultiViewBlockProperties
from ftw.simplelayout.tests import builders
from ftw.testing.layer import ComponentRegistryLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.dexterity.fti import DexterityFTI
from plone.testing import zca
from unittest2 import TestCase
from zope import schema
from zope.component import provideAdapter
from zope.configuration import xmlconfig
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

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.simplelayout:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        login(portal, TEST_USER_NAME)


class ISampleDX(Interface):
    title = schema.TextLine(
        title=u'Title',
        required=False)


class SampleBuilder(DexterityBuilder):
    portal_type = 'Sample'


registry.builder_registry.register('sample block', SampleBuilder)


class SimplelayoutTestCase(TestCase):

    def setup_sample_block_fti(self,
                               portal,
                               property_factory=MultiViewBlockProperties):

        types_tool = portal.portal_types

        self.fti = DexterityFTI('Sample')
        self.fti.schema = 'ftw.simplelayout.tests.test_ajax_change_block_view.ISampleDX'
        self.fti.behaviors = (
            'ftw.simplelayout.interfaces.ISimplelayoutBlock',
            'plone.app.lockingbehavior.behaviors.ILocking',)

        types_tool._setObject('Sample', self.fti)

        contentpage_fti = types_tool.get('ftw.simplelayout.ContentPage')
        contentpage_fti.allowed_content_types = (
            'ftw.simplelayout.tests.test_ajax_change_block_view.ISampleDX', )

        provideAdapter(property_factory,
                       adapts=(ISampleDX, Interface))

    def setup_block_views(self):

        class SampleBlockView(BaseBlock):

            def __call__(self):
                return 'OK'

        provideAdapter(SampleBlockView,
                       adapts=(ISampleDX, Interface),
                       provides=IBrowserView,
                       name='block_view')

        class SampleBlockViewDifferent(BaseBlock):

            def __call__(self):
                return 'OK - different view'

        provideAdapter(SampleBlockViewDifferent,
                       adapts=(ISampleDX, Interface),
                       provides=IBrowserView,
                       name='block_view_different')



FTW_SIMPLELAYOUT_FIXTURE = FtwSimplelayoutLayer()
FTW_SIMPLELAYOUT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_SIMPLELAYOUT_FIXTURE,), name="FtwSimplelayout:Integration")
FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_SIMPLELAYOUT_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name='FtwSimplelayout:Functional')

from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.simplelayout.tests import sample_types
from ftw.testing.layer import ComponentRegistryLayer
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from pkg_resources import get_distribution
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from plone.testing import z2
from plone.testing import zca
from unittest2 import TestCase
from zope.configuration import xmlconfig
import ftw.simplelayout.tests.builders  # noqa
import ftw.referencewidget.tests.widgets  # noqa


IS_PLONE_5 = get_distribution('Plone').version >= '5'


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

        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.simplelayout:lib')
        applyProfile(portal, 'plone.restapi:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        login(portal, TEST_USER_NAME)


class FtwSimplelayoutContentLayer(FtwSimplelayoutLayer):
    def setUpPloneSite(self, portal):

        if not IS_PLONE_5:
            applyProfile(portal, 'ftw.simplelayout.contenttypes:default')
            applyProfile(portal, 'ftw.simplelayout.mapblock:default')
            applyProfile(portal, 'ftw.simplelayout.aliasblock:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Site Administrator'])
        login(portal, TEST_USER_NAME)


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

    def assert_unwrapped_persistence(self, structure):
        def is_unwrapped(item):
            if not isinstance(item, basestring) and not isinstance(item, int):
                assert isinstance(item, dict) or \
                    isinstance(item, list), \
                    '{0} needs to be unwrapped'.format(str(item))

                if hasattr(item, 'values'):
                    item = item.values()
                for subitem in item:
                    is_unwrapped(subitem)
            else:
                return

        is_unwrapped(structure)

    def setup_sample_ftis(self, portal):
        sample_types.setup_ftis(portal)

    def setup_block_views(self):
        sample_types.setup_views()


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

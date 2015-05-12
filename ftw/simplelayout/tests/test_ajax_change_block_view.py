from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IBlockModifier
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.properties import SingleViewBlockProperties
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from ftw.simplelayout.testing import ISampleDX
from ftw.simplelayout.testing import SimplelayoutTestCase
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from zExceptions import BadRequest
from zope.component import provideAdapter
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
import json


class TestBlockReloadView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.contentpage = create(Builder('sl content page'))
        self.portal = self.layer['portal']

    def setup_block_views(self):

        class SampleBlockView(BrowserView):

            def __call__(self):
                return 'OK'

        provideAdapter(SampleBlockView,
                       adapts=(ISampleDX, Interface),
                       provides=IBrowserView,
                       name='block_view')

        class SampleBlockViewDifferent(BrowserView):

            def __call__(self):
                return 'OK - different view'

        provideAdapter(SampleBlockViewDifferent,
                       adapts=(ISampleDX, Interface),
                       provides=IBrowserView,
                       name='block_view_different')

    def get_reload_view(self, block, payload={}):
        payload['uid'] = IUUID(block)
        self.contentpage.REQUEST.set('data', json.dumps(payload))
        return self.contentpage.restrictedTraverse(
            '@@sl-ajax-reload-block-view')

    def test_getting_block_with_reload_view(self):
        self.setup_sample_block_fti(self.portal)
        self.setup_block_views()
        block = create(Builder('sample block').within(self.contentpage))
        reload_view = self.get_reload_view(block)
        reload_view()

        self.assertEquals(block, reload_view.block)

    def test_getting_block_properties_with_reload_view(self):
        self.setup_sample_block_fti(self.portal)
        self.setup_block_views()
        block = create(Builder('sample block').within(self.contentpage))
        reload_view = self.get_reload_view(block)
        reload_view()

        self.assertTrue(IBlockProperties.providedBy(reload_view.properties))

    def test_raise_bad_request_if_no_uid_is_in_payload(self):
        reload_view = self.contentpage.restrictedTraverse(
            '@@sl-ajax-reload-block-view')
        with self.assertRaises(BadRequest):
            reload_view()

    def test_return_value_is_the_block_content(self):
        self.setup_sample_block_fti(self.portal)
        self.setup_block_views()
        block = create(Builder('sample block').within(self.contentpage))
        reload_view = self.get_reload_view(block)

        self.assertEquals('OK', reload_view())

    def test_changing_block_view(self):
        self.setup_sample_block_fti(self.portal)
        self.setup_block_views()
        block = create(Builder('sample block').within(self.contentpage))
        reload_view = self.get_reload_view(
            block,
            dict(view_name='block_view_different'))

        self.assertEquals('OK - different view', reload_view())

    def test_chaning_block_on_singleviewblockproperties_is_NOT_possible(self):
        self.setup_sample_block_fti(self.portal,
                                    property_factory=SingleViewBlockProperties)
        self.setup_block_views()
        block = create(Builder('sample block').within(self.contentpage))
        reload_view = self.get_reload_view(
            block,
            dict(view_name='block_view_different'))

        with self.assertRaises(BadRequest):
            reload_view()

    def test_block_specific_modifier_gets_called(self):

        class SampleBlockModifier(object):
            """Sets the attribute foo to the given value"""

            implements(IBlockModifier)

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def modify(self, data):
                setattr(self.context, 'foo', data.get('foovalue', None))

        provideAdapter(SampleBlockModifier,
                       adapts=(ISampleDX, Interface),
                       provides=IBlockModifier)

        self.setup_sample_block_fti(self.portal)
        self.setup_block_views()
        block = create(Builder('sample block').within(self.contentpage))
        reload_view = self.get_reload_view(
            block,
            dict(foovalue='bar'))
        reload_view()

        self.assertEquals('bar', block.foo)

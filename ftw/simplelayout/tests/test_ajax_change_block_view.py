from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IBlockModifier
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from ftw.simplelayout.tests.sample_types import ISampleDXBlock
from ftw.simplelayout.testing import SimplelayoutTestCase
from plone.uuid.interfaces import IUUID
from zExceptions import BadRequest
from zope.component import provideAdapter
from zope.interface import implements
from zope.interface import Interface
import json


class TestBlockReloadView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()
        self.container = create(Builder('sample container'))

    def get_reload_view(self, block, payload={}):
        payload['uid'] = IUUID(block)
        self.container.REQUEST.set('data', json.dumps(payload))
        return self.container.restrictedTraverse(
            '@@sl-ajax-reload-block-view')

    def test_getting_block_with_reload_view(self):
        block = create(Builder('sample block').within(self.container))
        reload_view = self.get_reload_view(block)
        reload_view()

        self.assertEquals(block, reload_view.block)

    def test_getting_block_properties_with_reload_view(self):
        block = create(Builder('sample block').within(self.container))
        reload_view = self.get_reload_view(block)
        reload_view()

        self.assertTrue(IBlockProperties.providedBy(reload_view.properties))

    def test_raise_bad_request_if_no_uid_is_in_payload(self):
        reload_view = self.container.restrictedTraverse(
            '@@sl-ajax-reload-block-view')
        with self.assertRaises(BadRequest):
            reload_view()

    def test_return_value_is_the_block_content(self):
        block = create(Builder('sample block').within(self.container))
        reload_view = self.get_reload_view(block)

        self.assertEquals('OK', reload_view())

    def test_changing_block_view(self):
        block = create(Builder('sample block').within(self.container))
        reload_view = self.get_reload_view(
            block,
            dict(view_name='block_view_different'))

        self.assertEquals('OK - different view', reload_view())

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
                       adapts=(ISampleDXBlock, Interface),
                       provides=IBlockModifier)

        block = create(Builder('sample block').within(self.container))
        reload_view = self.get_reload_view(
            block,
            dict(foovalue='bar'))
        reload_view()

        self.assertEquals('bar', block.foo)

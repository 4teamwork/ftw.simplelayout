from Products.CMFCore.utils import getToolByName
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest
import json


class TestSaveStateView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        super(TestSaveStateView, self).setUp()

        portal = self.layer['portal']
        self.page = portal.get(portal.invokeFactory(
            'Page', 'the-page', title='The Page'))

        self.foo = self.page.get(self.page.invokeFactory(
                'Paragraph', 'foo', title='Foo'))

        self.bar = self.page.get(self.page.invokeFactory(
                'Paragraph', 'bar', title='bar'))

        self.baz = self.page.get(self.page.invokeFactory(
                'Paragraph', 'baz', title='Baz'))

    def tearDown(self):
        super(TestSaveStateView, self).tearDown()

        portal = self.layer['portal']
        portal.manage_delObjects(['the-page'])

    def get_content_ids(self):
        # Returns content ids of direct children using catalog.
        catalog = getToolByName(self.layer['portal'], 'portal_catalog')
        query = {'path': {'query': '/'.join(self.page.getPhysicalPath()),
                          'depth': 1},
                 'sort_on': 'getObjPositionInParent'}

        brains = catalog(query)

        return [brain.id for brain in brains]

    def generate_block_data(self, block, top=10, left=10, width=10,
                            height=10):
        return {'uuid': IUUID(block),
                'position': {'left': left,
                             'top': top},
                'size': {'width': width,
                         'height': height}}

    def test_view_registered(self):
        view = queryMultiAdapter((self.page, TestRequest()),
                                 name='sl-ajax-save-state')
        self.assertNotEqual(view, None)

    def test_view_fails_without_payload(self):
        view = getMultiAdapter((self.page, TestRequest()),
                                 name='sl-ajax-save-state')

        with self.assertRaises(BadRequest) as cm:
            view()

        self.assertEqual(
            str(cm.exception),
            'Request parameter "payload" not found.')

    def test_view_returns_OK(self):
        payload = [self.generate_block_data(self.foo)]
        request = TestRequest(form={'payload': json.dumps(payload)})

        view = getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')
        self.assertEqual(view(), 'OK')

    def test_content_order(self):
        self.assertEqual(self.get_content_ids(),
                         ['foo', 'bar', 'baz'])

        payload = [
            self.generate_block_data(self.baz),
            self.generate_block_data(self.foo),
            self.generate_block_data(self.bar),
            ]

        request = TestRequest(form={'payload': json.dumps(payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        self.assertEqual(self.get_content_ids(),
                         ['baz', 'foo', 'bar'])

    def test_block_positions(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                   IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                   IDisplaySettings)

        # Position is None when newer saved.
        self.assertEqual(foo_settings.get_position(), None)
        self.assertEqual(bar_settings.get_position(), None)


        # Set positions #1
        payload = [
            self.generate_block_data(self.foo, top=2, left=3.141592654),
            self.generate_block_data(self.bar, top=1, left=2),
            ]

        request = TestRequest(form={'payload': json.dumps(payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        # Check positions #1
        self.assertEqual(foo_settings.get_position(),
                         {'left': 3.141592654,
                          'top': 2})

        self.assertEqual(bar_settings.get_position(),
                         {'left': 2,
                          'top': 1})

        # Set positions #2
        payload = [
            self.generate_block_data(self.foo, top=11, left=12),
            self.generate_block_data(self.bar, top=13, left=14),
            ]

        request = TestRequest(form={'payload': json.dumps(payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        # Check positions #2
        self.assertEqual(foo_settings.get_position(),
                         {'left': 12,
                          'top': 11})

        self.assertEqual(bar_settings.get_position(),
                         {'left': 14,
                          'top': 13})

    def test_block_size(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                   IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                   IDisplaySettings)

        # Size is None when newer saved.
        self.assertEqual(foo_settings.get_size(), None)
        self.assertEqual(bar_settings.get_size(), None)


        # Set sizes #1
        payload = [
            self.generate_block_data(self.foo, height=2, width=3.141592654),
            self.generate_block_data(self.bar, height=1, width=2),
            ]

        request = TestRequest(form={'payload': json.dumps(payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        # Check sizes #1
        self.assertEqual(foo_settings.get_size(),
                         {'width': 3.141592654,
                          'height': 2})

        self.assertEqual(bar_settings.get_size(),
                         {'width': 2,
                          'height': 1})

        # Set sizes #2
        payload = [
            self.generate_block_data(self.foo, height=11, width=12),
            self.generate_block_data(self.bar, height=13, width=14),
            ]

        request = TestRequest(form={'payload': json.dumps(payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        # Check sizes #2
        self.assertEqual(foo_settings.get_size(),
                         {'width': 12,
                          'height': 11})

        self.assertEqual(bar_settings.get_size(),
                         {'width': 14,
                          'height': 13})

from ftw.builder import Builder
from ftw.builder import create
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

        self.page = create(Builder('sl content page').titled(u'The Page'))
        self.foo = create(Builder('sl textblock')
                          .within(self.page)
                          .titled(u'Foo'))
        self.bar = create(Builder('sl textblock')
                          .within(self.page)
                          .titled(u'Bar'))
        self.baz = create(Builder('sl textblock')
                          .within(self.page)
                          .titled(u'Baz'))

        self.layout_cache = []
        self.payload = {'blocks': [],
                        'layouts': []}

    def generate_block_data(self, block, height='auto', layout=0, column=0,
                            position=0, total_columns=1):

        self.payload['blocks'].append({'uid': IUUID(block),
                                       'height': height,
                                       'position': position,
                                       'layout': layout,
                                       'column': column,
                                       'total_columns': total_columns})

        if layout not in self.layout_cache:
            self.layout_cache.append(layout)
            self.payload['layouts'].append(total_columns)

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
        self.generate_block_data(self.foo)
        request = TestRequest(form={'payload': json.dumps(self.payload)})

        view = getMultiAdapter((self.page, request),
                               name='sl-ajax-save-state')
        self.assertEqual('{"Status": "OK", "msg": "Saved state of 1 blocks"}',
                         view())

    def test_setting_block_position(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                       IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                       IDisplaySettings)

        self.generate_block_data(self.foo, position=1),
        self.generate_block_data(self.bar, position=0),

        request = TestRequest(form={'payload': json.dumps(self.payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        self.assertEqual(foo_settings.get_position(), 1)
        self.assertEqual(bar_settings.get_position(), 0)

    def test_setting_block_height(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                       IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                       IDisplaySettings)

        self.generate_block_data(self.foo, height='auto',),
        self.generate_block_data(self.bar, height=100,),

        request = TestRequest(form={'payload': json.dumps(self.payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        self.assertEqual(foo_settings.get_height(), 'auto')
        self.assertEqual(bar_settings.get_height(), 100)

    def test_setting_block_layout(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                       IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                       IDisplaySettings)

        self.generate_block_data(self.foo, layout=0,),
        self.generate_block_data(self.bar, layout=1,),

        request = TestRequest(form={'payload': json.dumps(self.payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        self.assertEqual(foo_settings.get_layout(), 0)
        self.assertEqual(bar_settings.get_layout(), 1)

    def test_setting_block_column(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                       IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                       IDisplaySettings)

        self.generate_block_data(self.foo, column=0,),
        self.generate_block_data(self.bar, column=1,),

        request = TestRequest(form={'payload': json.dumps(self.payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        self.assertEqual(foo_settings.get_column(), 0)
        self.assertEqual(bar_settings.get_column(), 1)

    def test_setting_total_columns(self):
        foo_settings = getMultiAdapter((self.foo, TestRequest()),
                                       IDisplaySettings)
        bar_settings = getMultiAdapter((self.bar, TestRequest()),
                                       IDisplaySettings)

        self.generate_block_data(self.foo, layout=0, total_columns=2,),
        self.generate_block_data(self.bar, layout=1, total_columns=4,),

        request = TestRequest(form={'payload': json.dumps(self.payload)})
        getMultiAdapter((self.page, request),
                        name='sl-ajax-save-state')()

        self.assertEqual(foo_settings.get_total_columns(), 2)
        self.assertEqual(bar_settings.get_total_columns(), 4)

        # Cross check the layout config of generate_block_data
        self.assertEquals(self.payload['layouts'], [2, 4])

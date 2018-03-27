from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from unittest2 import TestCase


class TestNameChooser(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestNameChooser, self).setUp()
        self.portal = self.layer['portal']

    def test_creating_content_named_layout(self):
        page = create(Builder('sl content page').titled(u'Layout'))
        self.assertEqual(
            'layout-1',
            page.getId()
        )

    def test_creating_content_named_simplelayout(self):
        page = create(Builder('sl content page').titled(u'Simplelayout'))
        self.assertEqual(
            'simplelayout-1',
            page.getId()
        )

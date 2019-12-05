from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.properties import BLOCK_PROPERTIES_KEY
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.utils import get_block_html
from ftw.testbrowser import browsing
from Persistence import PersistentMapping
from unittest import TestCase
from zope.annotation import IAnnotations


class TestUtils(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    @browsing
    def test_get_html_block_with_unicode_viewname(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock')
                       .within(page)
                       .titled(u'My Text Block'))

        # Set a unicode view name.
        annotations = IAnnotations(block)
        if BLOCK_PROPERTIES_KEY not in annotations:
            annotations[BLOCK_PROPERTIES_KEY] = PersistentMapping({
                'view-name': u'block_view'
            })

        self.assertIn(u'My Text Block', get_block_html(block))

from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from unittest2 import TestCase


class TestAddableBlocksView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        super(TestAddableBlocksView, self).setUp()

    def test_addable_blocks_view(self):
        page = create(Builder('sl content page'))

        view = page.restrictedTraverse('@@addable-blocks-view')

        allowed_block_types = view.addable_blocks()
        result = list(allowed_block_types)
        result.sort()

        self.assertEquals(
            ['ftw.simplelayout.TextBlock', ],
            result)

    def test_addable_blocks_view_renders(self):
        page = create(Builder('sl content page'))
        view = page.restrictedTraverse('@@addable-blocks-view')
        self.assertTrue(len(view()), 'Cannot render view.')

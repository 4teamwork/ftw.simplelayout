from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.properties import MultiViewBlockProperties
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestMultiViewBlockProperties(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.setup_sample_ftis(self.layer['portal'])
        contentpage = create(Builder('sample container'))
        self.setup_block_views()
        self.block = create(Builder('sample block').within(contentpage))

    def test_implements_interface(self):
        verifyClass(IBlockProperties, MultiViewBlockProperties)

    def test_get_current_default_block_view(self):
        properties = getMultiAdapter((self.block, self.block.REQUEST),
                                     IBlockProperties)

        self.assertEqual(properties.get_current_view_name(),
                         'block_view')

    def test_changing_view(self):
        properties = getMultiAdapter((self.block, self.block.REQUEST),
                                     IBlockProperties)

        properties.set_view('block_view_different')
        self.assertEqual(properties.get_current_view_name(),
                         'block_view_different')

    def test_setting_invalid_view_name_raises_error(self):
        properties = getMultiAdapter((self.block, self.block.REQUEST),
                                     IBlockProperties)

        with self.assertRaises(ValueError) as cm:
            properties.set_view('unkown-view')
        self.assertEqual(str(cm.exception),
                         '"unkown-view" is not in available views.')

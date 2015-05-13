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
        super(TestMultiViewBlockProperties, self).setUp()
        contentpage = create(Builder('sl content page'))

        self.setup_sample_block_fti(self.layer['portal'])
        self.setup_block_views()
        self.block = create(Builder('sample block').within(contentpage))

    def test_implements_interface(self):
        verifyClass(IBlockProperties, MultiViewBlockProperties)

    def test_get_current_default_block_view(self):
        properties = getMultiAdapter((self.block, self.block.REQUEST),
                                     IBlockProperties)

        self.assertEqual(properties.get_current_view_name(),
                         'block_view')

    def test_get_available_views(self):
        properties = getMultiAdapter((self.block, self.block.REQUEST),
                                     IBlockProperties)
        self.assertEquals(['block_view_different', 'block_view'],
                          properties.get_available_views())

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

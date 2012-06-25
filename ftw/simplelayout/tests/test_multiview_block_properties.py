from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.properties import MultiViewBlockProperties
from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.annotation import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import Interface
from zope.interface.verify import verifyClass


class IFoo(IAttributeAnnotatable):
    """
    """


class FooBlockProperties(MultiViewBlockProperties):

    available_views = (
        {'name': 'block_view',
         'label': u'Default block view'},

        {'name': 'foo_view',
         'label': u'Foo view'})


class TestMultiViewBlockProperties(MockTestCase):

    layer = SIMPLELAYOUT_ZCML_LAYER

    def setUp(self):
        super(TestMultiViewBlockProperties, self).setUp()

        self.context = self.providing_stub(IFoo)
        self.request = self.stub_request()

        provideAdapter(FooBlockProperties, adapts=(IFoo, Interface))

    def test_implements_interface(self):
        self.replay()
        verifyClass(IBlockProperties, MultiViewBlockProperties)

    def test_get_current_view_name_default_view(self):
        self.replay()
        # default view is "block_view"

        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        self.assertEqual(properties.get_current_view_name(),
                         'block_view')

    def test_get_available_views(self):
        self.replay()

        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        self.assertEqual(
            properties.get_available_views(), (
                {'name': 'block_view',
                 'label': u'Default block view'},

                {'name': 'foo_view',
                 'label': u'Foo view'}))

    def test_changing_view(self):
        self.replay()

        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        self.assertEqual(properties.get_current_view_name(), 'block_view')

        with self.assertRaises(ValueError) as cm:
            properties.set_view('unkown-view')
        self.assertEqual(str(cm.exception),
                         '"unkown-view" is not in available views.')

        properties.set_view('foo_view')
        self.assertEqual(properties.get_current_view_name(), 'foo_view')

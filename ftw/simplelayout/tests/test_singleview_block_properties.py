from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.properties import SingleViewBlockProperties
from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import Interface
from zope.interface.verify import verifyClass


class IFoo(Interface):
    """
    """


class TestSingleViewBlockProperties(MockTestCase):

    layer = SIMPLELAYOUT_ZCML_LAYER

    def setUp(self):
        super(TestSingleViewBlockProperties, self).setUp()

        self.context = self.providing_stub(IFoo)
        self.request = self.stub_request()

        provideAdapter(SingleViewBlockProperties, adapts=(IFoo, Interface))

    def test_implements_interface(self):
        self.replay()
        verifyClass(IBlockProperties, SingleViewBlockProperties)

    def test_get_current_view_name(self):
        self.replay()
        # defaults to "block_view"

        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        self.assertEqual(properties.get_current_view_name(),
                         'block_view')

    def test_get_avaiable_views_returns_None(self):
        self.replay()
        # single view adapter: views are not selectable -> should return None

        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        self.assertEqual(properties.get_available_views(), None)

    def test_set_view_raises_error(self):
        self.replay()
        # single view adapter: setting view is not supported

        properties = getMultiAdapter((self.context, self.request),
                                     IBlockProperties)

        with self.assertRaises(RuntimeError) as cm:
            properties.set_view('foo')

        self.assertEqual(
            str(cm.exception),
            'SingleViewBlockProperties adapter does not support setting '
            'the view.')

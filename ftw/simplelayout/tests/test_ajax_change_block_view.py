from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.properties import MultiViewBlockProperties
from ftw.simplelayout.properties import SingleViewBlockProperties
from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.testing import MockTestCase
from zExceptions import BadRequest
from zope.annotation import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.component import queryMultiAdapter
from zope.interface import Interface


class IFoo(IAttributeAnnotatable):
    pass


class IBar(IAttributeAnnotatable):
    pass


class FooBlockProperties(MultiViewBlockProperties):

    available_views = (
        {'name': 'block_view',
         'label': u'Default block view'},

        {'name': 'foo_view',
         'label': u'Foo view'})


class TestChangeBlockView(MockTestCase):

    layer = SIMPLELAYOUT_ZCML_LAYER

    def setUp(self):
        super(TestChangeBlockView, self).setUp()
        self.foo = self.providing_stub(IFoo)
        provideAdapter(FooBlockProperties, adapts=(IFoo, Interface))

        self.expect(
            self.foo.restrictedTraverse('@@block_view')()).result(
            'The block_view rendered.')

        self.expect(
            self.foo.restrictedTraverse('@@foo_view')()).result(
            'The foo_view rendered.')

        self.expect(
            self.foo.restrictedTraverse('@@bar_view')).throw(
            AttributeError('bar_view'))

        self.bar = self.providing_stub(IBar)
        provideAdapter(SingleViewBlockProperties, adapts=(IBar, Interface))

        self.request = self.stub_request()

    def test_view_registered(self):
        self.replay()
        view = queryMultiAdapter((self.foo, self.request),
                                 name='sl-ajax-change-block-view')
        self.assertNotEqual(view, None)

    def test_changing_view_is_persistent(self):
        self.expect(self.request.get('view_name', None)).result('foo_view')
        self.replay()

        properties = getMultiAdapter((self.foo, self.request),
                                     IBlockProperties)
        self.assertEqual(properties.get_current_view_name(), 'block_view')

        view = getMultiAdapter((self.foo, self.request),
                               name='sl-ajax-change-block-view')
        view()

        properties = getMultiAdapter((self.foo, self.request),
                                     IBlockProperties)
        self.assertEqual(properties.get_current_view_name(), 'foo_view')

    def test_change_view_returns_new_view_rendered(self):
        self.expect(self.request.get('view_name', None)).result('foo_view')
        self.replay()

        view = getMultiAdapter((self.foo, self.request),
                               name='sl-ajax-change-block-view')
        self.assertEqual(view(), 'The foo_view rendered.')

    def test_change_to_wrong_view_fails(self):
        self.expect(self.request.get('view_name', None)).result('baz-view')
        self.replay()

        view = getMultiAdapter((self.foo, self.request),
                               name='sl-ajax-change-block-view')

        with self.assertRaises(BadRequest) as cm:
            view()

        self.assertEqual(
            str(cm.exception),
            'The view "baz-view" is not available on this block.')

    def test_view_name_not_in_request(self):
        self.expect(self.request.get('view_name', None)).result(None)
        self.replay()

        view = getMultiAdapter((self.foo, self.request),
                               name='sl-ajax-change-block-view')

        with self.assertRaises(BadRequest) as cm:
            view()

        self.assertEqual(
            str(cm.exception),
            'Request parameter "view_name" not found.')

    def test_single_view_blocks_not_supported(self):
        self.expect(self.request.get('view_name', None)).result('baz-view')
        self.replay()

        view = getMultiAdapter((self.bar, self.request),
                               name='sl-ajax-change-block-view')

        with self.assertRaises(BadRequest) as cm:
            view()

        self.assertEqual(
            str(cm.exception),
            'This object does not support changing the view.')

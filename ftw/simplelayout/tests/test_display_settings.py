from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.annotation import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface.verify import verifyClass
from Persistence import PersistentMapping


class TestDisplaySettings(MockTestCase):

    layer = SIMPLELAYOUT_ZCML_LAYER

    def setUp(self):
        super(TestDisplaySettings, self).setUp()

        self.context = self.providing_stub(IAttributeAnnotatable)
        self.request = self.stub_request()

    def test_component_registered(self):
        self.replay()
        component = queryMultiAdapter((self.context, self.request),
                                      IDisplaySettings)
        self.assertNotEqual(component, None)

    def test_implements_interface(self):
        self.replay()
        component = queryMultiAdapter((self.context, self.request),
                                      IDisplaySettings)
        verifyClass(IDisplaySettings, component.__class__)

    def test_position(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_position(), None)
        settings.set_position(1)
        self.assertEqual(settings.get_position(), 1)

    def test_height(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_height(), None)
        settings.set_height('auto')
        self.assertEqual(settings.get_height(), 'auto')

    def test_layout(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_layout(), None)
        settings.set_layout(2)
        self.assertEqual(settings.get_layout(), 2)

    def test_column(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_column(), None)
        settings.set_column(4)
        self.assertEqual(settings.get_column(), 4)

    def test_total_columns(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_total_columns(), None)
        settings.set_total_columns(1)
        self.assertEqual(settings.get_total_columns(), 1)

    def test_setter_conditions(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)
        with self.assertRaises(ValueError):
            settings.set_position('Not a integer')
        with self.assertRaises(ValueError):
            settings.set_layout('Not a integer')
        with self.assertRaises(ValueError):
            settings.set_column('Not a integer')
        with self.assertRaises(ValueError):
            settings.set_total_columns('Not a integer')

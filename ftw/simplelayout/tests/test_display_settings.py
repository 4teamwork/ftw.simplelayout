from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.app.annotation.interfaces import IAttributeAnnotatable
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
        component = queryMultiAdapter((self.context, self.request),
                                      IDisplaySettings)
        self.assertNotEqual(component, None)

    def test_implements_interface(self):
        component = queryMultiAdapter((self.context, self.request),
                                      IDisplaySettings)
        verifyClass(IDisplaySettings, component.__class__)

    def test_position(self):
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_position(), None)
        settings.set_position({'top': 10, 'left': 30.7})
        self.assertEqual(settings.get_position(), {'top': 10, 'left': 30.7})
        self.assertTrue(isinstance(settings.get_position(), PersistentMapping))

    def test_size(self):
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_size(), None)
        settings.set_size({'width': 100, 'height': 50.3})
        self.assertEqual(settings.get_size(), {'width': 100, 'height': 50.3})
        self.assertTrue(isinstance(settings.get_size(), PersistentMapping))

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
        settings.set_position({'top': 10, 'left': 30.7})
        self.assertEqual(settings.get_position(), {'top': 10, 'left': 30.7})
        self.assertTrue(isinstance(settings.get_position(), PersistentMapping))

    def test_size(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertEqual(settings.get_size(), None)
        settings.set_size({'width': 100, 'height': 50.3})
        self.assertEqual(settings.get_size(), {'width': 100, 'height': 50.3})
        self.assertTrue(isinstance(settings.get_size(), PersistentMapping))

    def test_setter_condition(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)
        with self.assertRaises(ValueError):
            settings.set_size({'foo': 100})
        with self.assertRaises(ValueError):
            settings.set_position({'foo': 100})

    def test_imagestyles_getter_default(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        self.assertIsNone(settings.get_image_styles())

    def test_imagestyles_setter(self):
        self.replay()
        settings = getMultiAdapter((self.context, self.request),
                                   IDisplaySettings)

        settings.set_image_styles('width:100px;')
        self.assertEquals('width:100px;', settings.get_image_styles())

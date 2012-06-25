from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.component import queryMultiAdapter
from zope.annotaions import IAttributeAnnotable


class TestDisplaySettings(MockTestCase):

    layer = SIMPLELAYOUT_ZCML_LAYER

    def setUp(self):
        MockTestCase.setUp(self)

        self.context = self.proveding_stub(IAttributeAnnotable)
        self.request = self.stub_request()

    def test_component_registered(self):
        component = queryMultiAdapter((self.context, self.request), IDisplaySettings)
        self.assertNotEqual(component, None)

    def test_implements_interface(self):
        component = queryMultiAdapter((self.context, self.request), IDisplaySettings)
        verifyClass(IDisplaySettings, component.__class__)

    def test_position(self):
        settings = getMultiAdapter((self.context, self.request), IDisplaySettings)

        self.assertEqual(settings.get_display(), None)
        settings.set_display({'top': 10, 'left': 30.7})
        self.assertEqual(settings.get_display(), {'top': 10, 'left': 30.7})

    def test_size(self):
        settings = getMultiAdapter((self.context, self.request), IDisplaySettings)

        self.assertEqual(settings.get_size(), None)
        settings.set_size({'width': 100, 'height': 50.3})
        self.assertEqual(settings.get_size(), {'width': 100, 'height': 50.3})

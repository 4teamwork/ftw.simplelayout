from ftw.simplelayout.testing import SIMPLELAYOUT_ZCML_LAYER
from ftw.testing import MockTestCase
from mocker import ANY
from zope.component import getMultiAdapter



class TestBlocksAdapters(MockTestCase):

    layer = SIMPLELAYOUT_ZCML_LAYER

    def setUp(self):
        MockTestCase.setUp(self)



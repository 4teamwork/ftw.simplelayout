from plone.testing import zca
from ftw.testing.layer import ComponentRegistryLayer


class SimplelayoutZCMLLayer(ComponentRegistryLayer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def setUp(self):
        super(SimplelayoutZCMLLayer, self).setUp()

        import ftw.simplelayout.tests
        self.load_zcml_file('tests.zcml', ftw.simplelayout.tests)

SIMPLELAYOUT_ZCML_LAYER = SimplelayoutZCMLLayer()

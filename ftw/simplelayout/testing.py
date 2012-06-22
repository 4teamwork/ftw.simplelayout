from plone.testing import Layer
from plone.testing import zca
from zope.configuration import xmlconfig


class SimplelayoutZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        import zope.traversing
        xmlconfig.file('configure.zcml', zope.traversing,
                       context=self['configurationContext'])


    def testTearDown(self):
        del self['configurationContext']


SIMPLELAYOUT_ZCML_LAYER = SimplelayoutZCMLLayer()

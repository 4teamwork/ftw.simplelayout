from zope.component import getMultiAdapter
from ftw.simplelayout.opengraph.interfaces import IOpenGraphDataProvider
from plone.app.layout.viewlets.common import ViewletBase


class OpenGraph(ViewletBase):

    def index(self):
        return '\n'.join(map(
            lambda og: u'<meta property="{0}" content="{1}" />'.format(*og),
            self.get_og_data().items()))

    def get_og_data(self):
        return getMultiAdapter((self.context, self.request, self.view),
                               IOpenGraphDataProvider, name="opengraph")()

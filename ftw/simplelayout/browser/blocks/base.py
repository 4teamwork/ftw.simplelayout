from Products.Five.browser import BrowserView
from ftw.simplelayout.interfaces import IBlockConfiguration


class BaseBlock(BrowserView):

    blockconfig = None

    def __init__(self, context, request):
        super(BaseBlock, self).__init__(context, request)

        self.blockconfig = IBlockConfiguration(self.context).load()

    def __call__(self):
        return self.template()

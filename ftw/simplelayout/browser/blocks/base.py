from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutBlockView
from Products.Five.browser import BrowserView
from zope.interface import implements


class BaseBlock(BrowserView):
    implements(ISimplelayoutBlockView)

    blockconfig = None

    def __init__(self, context, request):
        super(BaseBlock, self).__init__(context, request)

        self.blockconfig = IBlockConfiguration(self.context).load()

    def __call__(self):
        return self.template()

    @property
    def block_title(self):
        """
        This property returns the title only if the title should be shown
        and the title has a value.
        """
        title = getattr(self.context, 'title', '')
        show_title = getattr(self.context, 'show_title', True)

        if show_title and title:
            return title
        return ''

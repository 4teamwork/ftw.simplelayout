from ftw.simplelayout.interfaces import ISimplelayoutBlock
from Products.Five.browser import BrowserView
from Products.TinyMCE.browser.interfaces.anchors import IAnchorView
from zope.interface import implements


class BlockAnchorsView(BrowserView):
    implements(IAnchorView)

    def listAnchorNames(self, *args, **kwargs):
        anchors = []
        query = {'object_provides': ISimplelayoutBlock.__identifier__}

        for block in self.context.listFolderContents(contentFilter=query):
            view = block.restrictedTraverse('content_anchors')
            anchors.extend(view.listAnchorNames(*args, **kwargs))

        return anchors

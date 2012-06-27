from AccessControl import getSecurityManager
from AccessControl.SpecialUsers import nobody
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.interfaces import ISimplelayoutView
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView


class SimplelayoutView(BrowserView):
    implements(ISimplelayoutView)

    def get_blocks(self):
        user = getSecurityManager().getUser()

        for block in self.context.listFolderContents():
            properties = queryMultiAdapter((block, self.request),
                                           IBlockProperties)
            if properties is None:
                continue

            view_name = properties.get_current_view_name()
            view = block.restrictedTraverse(view_name)

            display_settings = queryMultiAdapter((block, self.request),
                                                 IDisplaySettings)

            yield {
                'block': block,
                'view': view,
                'available_views': properties.get_available_views(),
                'position': display_settings.get_position(),
                'size': display_settings.get_size(),
                'editable': user is not nobody and user.has_permission(
                    'cmf.ModifyPortalContent', block)}

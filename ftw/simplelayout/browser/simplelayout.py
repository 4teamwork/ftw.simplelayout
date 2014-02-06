from AccessControl import getSecurityManager
from AccessControl.SpecialUsers import nobody
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.interfaces import ISimplelayoutView
from plone.uuid.interfaces import IUUID
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView


STYLE_ATTRIBUTE = ('top:{top}px;'
                   'left:{left}px;'
                   'width:{width}px;'
                   'height:{height}px;')


def get_style(settings):
    position = settings.get_position()
    size = settings.get_size()

    if position and size:
        return STYLE_ATTRIBUTE.format(
            **{'top': position['top'],
               'left': position['left'],
               'width': size['width'],
               'height': size['height']})


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
                'uuid': IUUID(block),
                'view': view,
                'available_views': properties.get_available_views(),
                'position': display_settings.get_position(),
                'size': display_settings.get_size(),
                'style': get_style(display_settings),
                'editable': user is not nobody and user.has_permission(
                    'cmf.ModifyPortalContent', block)}

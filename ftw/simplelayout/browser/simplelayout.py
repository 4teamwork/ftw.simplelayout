from AccessControl import getSecurityManager
from AccessControl.SpecialUsers import nobody
from ftw.simplelayout.interfaces import IBlockProperties
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.interfaces import ISimplelayoutView
from plone import api
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.browser import BrowserView


STYLE_ATTRIBUTE = ('top:{top}px;'
                   'left:{left}px;'
                   'width:{width}px;'
                   'height:{height}px;')

CONFIG_TEMPLATE = ('{{"columns": {columns}, '
                   '"images": {images}, '
                   '"contentwidth": {contentwidth}, '
                   '"margin_right": {margin_right}, '
                   '"contentarea": "{contentarea}", '
                   '"editable": {editable}}}')


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

    columns = None

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

    def can_modify(self):
        return not api.user.is_anonymous() and api.user.get_permissions(
            obj=self.context)['Modify portal content']

    def load_default_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimplelayoutDefaultSettings)

        return CONFIG_TEMPLATE.format(
            **{'columns': self.columns or settings.columns,
               'images': settings.images,
               'contentwidth': settings.contentwidth,
               'margin_right': settings.margin_right,
               'contentarea': settings.contentarea,
               'editable': str(self.can_modify()).lower()})

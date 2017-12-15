from collective.geo.mapwidget.browser.widget import MapWidget
from ftw.simplelayout.browser.blocks.base import BaseBlock
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BlockMapWidget(MapWidget):

    def map_defaults(self):
        defaults = super(BlockMapWidget, self).map_defaults()

        zoom = getattr(self.context, 'zoomlevel', None)
        if zoom is not None:
            defaults['zoom'] = zoom

        maplayer = getattr(self.context, 'maplayer', None)
        if maplayer is not None:
            defaults['maplayer'] = maplayer

        return defaults


class MapBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/mapblock.pt')

    def get_address_map(self):
        address_map = BlockMapWidget(self, self.request, self.context)
        address_map.mapid = "geo-%s" % self.context.getId()
        address_map.addClass('block-map')
        address_map.klass = 'blockwidget-cgmap'

        return address_map

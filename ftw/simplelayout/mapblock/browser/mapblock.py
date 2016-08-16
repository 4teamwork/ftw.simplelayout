from ftw.simplelayout.browser.blocks.base import BaseBlock
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.geo.mapwidget.browser.widget import MapWidget


class MapBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/mapblock.pt')

    def get_address_map(self):
        address_map = MapWidget(self, self.request, self.context)
        address_map.mapid = "geo-%s" % self.context.getId()
        address_map.addClass('block-map')
        address_map.klass = 'blockwidget-cgmap'

        return address_map

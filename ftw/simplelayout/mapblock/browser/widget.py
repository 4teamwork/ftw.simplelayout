from collective.geo.mapwidget.browser.widget import MapLayers
from collective.z3cform.mapwidget.widget import FormMapWidget
from collective.z3cform.mapwidget.widget import IFormMapWidget
from collective.z3cform.mapwidget.widget import MapDisplayWidget
from ftw.simplelayout.mapblock.browser.mapblock import BlockMapWidget
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.schema.interfaces import IField


class IBlockFormMapWidget(IFormMapWidget):
    """Marker interface for z3c form block map widget"""
    pass


class BlockFormMapWidget(FormMapWidget):
    implementsOnly(IBlockFormMapWidget)

    @property
    def cgmap(self):
        if self.mode == DISPLAY_MODE:
            return MapDisplayWidget(self, self.request, self.context)
        return BlockMapWidget(self, self.request, self.context)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def BlockMapFieldWidget(field, request):
    """IFieldWidget factory for FormMapWidget."""
    return FieldWidget(field, BlockFormMapWidget(request))


class FixedMapLayers(MapLayers):

    @property
    def js(self):
        layers = self.layers()
        return """
$(window).bind('mapload', function (evt, widget) {
    // INFO: No longer load more layers if they're already there.
    if (widget.map.layers.length !== 0) {
        return;
    }

    widget.addLayers([
        %(layers)s
    ], '%(mapid)s');
});

""" % {
            'layers': ",\n".join([l.jsfactory for l in layers]),
            'mapid': self.widget.mapid
        }

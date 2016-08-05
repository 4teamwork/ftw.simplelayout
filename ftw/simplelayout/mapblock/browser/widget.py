from collective.z3cform.mapwidget.widget import FormMapWidget
from collective.z3cform.mapwidget.widget import IFormMapWidget
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


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def BlockMapFieldWidget(field, request):
    """IFieldWidget factory for FormMapWidget."""
    return FieldWidget(field, BlockFormMapWidget(request))

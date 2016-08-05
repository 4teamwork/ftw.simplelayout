from collective.geo.behaviour import MessageFactory as _
from ftw.simplelayout.mapblock.browser.widget import BlockMapFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class IBlockCoordinates(model.Schema):
    """Add coordinates and map styles to content
    """

    coordinates = schema.Text(
        title=_(u"Coordinates"),
        description=_(u"Modify geographical data for this content"),
        required=False,
    )

    form.widget(
        coordinates=BlockMapFieldWidget
    )

    model.fieldset(
        'coordinates',
        label=_(u'Coordinates'),
        fields=('coordinates', )
    )


alsoProvides(IBlockCoordinates, IFormFieldProvider)

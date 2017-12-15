from collective.geo.behaviour import MessageFactory as _
from ftw.simplelayout.mapblock.contents.interfaces import IMapBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IMapBlockSchema(form.Schema):
    """MapBlock for simplelayout
    """

    form.mode(zoomlevel='hidden')
    zoomlevel = schema.TextLine(
        title=u"Zoom",
        required=False,
    )

    form.mode(maplayer='hidden')
    maplayer = schema.TextLine(
        title=u"Maplayer",
        required=False,
    )

    model.fieldset(
        'coordinates',
        label=_(u'Coordinates'),
        fields=('zoomlevel', 'maplayer')
    )


alsoProvides(IMapBlockSchema, IFormFieldProvider)


class MapBlock(Item):
    implements(IMapBlock)

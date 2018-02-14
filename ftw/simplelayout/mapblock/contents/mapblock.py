from collective.geo.behaviour import MessageFactory as CGMF
from ftw.simplelayout import _
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

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True,
        required=False)

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
        label=CGMF(u'Coordinates'),
        fields=('zoomlevel', 'maplayer', 'title', 'show_title')
    )


alsoProvides(IMapBlockSchema, IFormFieldProvider)


class MapBlock(Item):
    implements(IMapBlock)

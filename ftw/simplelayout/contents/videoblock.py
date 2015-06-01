from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import IVideoBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IVideoBlockSchema(form.Schema):
    """MapBlock for simplelayout
    """

    video_url = schema.URI(
        title=_(u'Video URL', default=u'Youtube, or Vimeo URL'),
        required=True)

alsoProvides(IVideoBlockSchema, IFormFieldProvider)


class VideoBlock(Item):
    implements(IVideoBlock)

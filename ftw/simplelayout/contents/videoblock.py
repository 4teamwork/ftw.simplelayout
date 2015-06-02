from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import IVideoBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from urlparse import urlparse


def is_youtube_url(url):
    # https://youtu.be/W42x6-Wf3Cs
    parsed_url = urlparse(url)
    path = parsed_url.path.split('/')
    return parsed_url.netloc == 'youtu.be' and len(path) == 2


class IVideoBlockSchema(form.Schema):
    """MapBlock for simplelayout
    """

    video_url = schema.URI(
        title=_(u'Video URL', default=u'Youtube, or Vimeo URL'),
        required=True)

    @invariant
    def validate_video_url(data):
        if not is_youtube_url(data.video_url):
            raise Invalid(_(u'This is no a valid youtube, or vimeo url.'))

alsoProvides(IVideoBlockSchema, IFormFieldProvider)


class VideoBlock(Item):
    implements(IVideoBlock)

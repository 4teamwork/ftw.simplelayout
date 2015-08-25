from ftw.simplelayout import _
from ftw.simplelayout.contenttypes.contents.interfaces import IVideoBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from urlparse import urlparse
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant


def is_vimeo_url(url):
    # https://vimeo.com/channels/staffpicks/128510631
    parsed_url = urlparse(url)
    path = parsed_url.path.split('/')
    return parsed_url.netloc == 'vimeo.com' and path[-1].isdigit()


def is_youtube_url(url):
    # https://youtu.be/W42x6-Wf3Cs
    parsed_url = urlparse(url)
    path = parsed_url.path.split('/')
    return parsed_url.netloc == 'youtu.be' and len(path) == 2 and path[-1]


class IVideoBlockSchema(form.Schema):
    """VideoBlock for simplelayout
    """

    video_url = schema.URI(
        title=_(u'label_video_url', default=u'Youtube, or Vimeo URL'),
        description=_(u'Youtube format: http(s)://youtu.be/VIDEO_ID<br/>'
                      u'Vimeo format: http(s)://vimeo.com/(channels/groups)/'
                      u'VIDEO_ID'),
        required=True)

    @invariant
    def validate_video_url(data):
        if is_youtube_url(data.video_url):
            return
        elif is_vimeo_url(data.video_url):
            return
        else:
            raise Invalid(_(u'This is no a valid youtube, or vimeo url.'))

alsoProvides(IVideoBlockSchema, IFormFieldProvider)


class VideoBlock(Item):
    implements(IVideoBlock)

from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.contenttypes.contents.videoblock import is_vimeo_url
from ftw.simplelayout.contenttypes.contents.videoblock import is_youtube_url
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urlparse import urlparse
import json


VIMEO_PLAYER = "//player.vimeo.com/video/{0}"


class VideoBlockView(BaseBlock):

    youtube_template = ViewPageTemplateFile('templates/videoblock_youtube.pt')
    vimeo_template = ViewPageTemplateFile('templates/videoblock_vimeo.pt')

    template = None

    def __call__(self):
        if is_youtube_url(self.context.video_url):
            self.template = self.youtube_template
        elif is_vimeo_url(self.context.video_url):
            self.template = self.vimeo_template
        else:
            raise ValueError("No template found.")

        return super(VideoBlockView, self).__call__()

    def get_uuid(self):
        return 'uuid_{0}'.format(IUUID(self.context))

    def youtube_config(self):
        config = {'videoId': self.get_video_id(),
                  'width': '100%'}

        return json.dumps(config)

    def vimeo_player(self):
        return VIMEO_PLAYER.format(self.get_video_id())

    def get_video_id(self):
        if is_youtube_url(self.context.video_url):
            parsed_url = urlparse(self.context.video_url)
            return parsed_url.path[1:]
        elif is_vimeo_url(self.context.video_url):
            parsed_url = urlparse(self.context.video_url)
            path = parsed_url.path.split('/')
            return path[-1]
        else:
            return None

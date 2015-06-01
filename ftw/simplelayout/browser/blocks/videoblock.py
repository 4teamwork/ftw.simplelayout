from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import json
from urlparse import urlparse


class VideoBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/videoblock.pt')

    def get_uuid(self):
        return IUUID(self.context)

    def youtube_config(self):
        config = {'videoId': self.get_video_id(),
                  'width': '100%'}

        return json.dumps(config)

    def get_video_id(self):
        # https://youtu.be/W42x6-Wf3Cs
        parsed_url = urlparse(self.context.video_url)
        return parsed_url.path[1:]

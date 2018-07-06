from plone.restapi.services import Service
from ftw.simplelayout.configuration import synchronize_page_config_with_blocks


class SynchronizePageConfigWithBlocks(Service):

    def reply(self):
        return synchronize_page_config_with_blocks(self.context)

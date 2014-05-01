from ftw.simplelayout.interfaces import IBlockProperties
from plone.app.uuid.utils import uuidToObject
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView


class BlockControls(BrowserView):

    template = ViewPageTemplateFile('templates/controls.pt')

    def __init__(self, context, request):
        super(BlockControls, self).__init__(context, request)
        self.block = None

    def __call__(self):
        uuid = self.request.get('uuid', None)
        if uuid is None:
            raise BadRequest('No uuid provided.')

        block = uuidToObject(uuid)

        if not block:
            raise BadRequest('Block not found.')

        self.block = block
        return self.template()

    def views(self):
        properties = queryMultiAdapter((self.block, self.request),
                                       IBlockProperties)

        return properties.get_available_views()

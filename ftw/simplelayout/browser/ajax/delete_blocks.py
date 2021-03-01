from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.utils import IS_PLONE_5
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import BadRequest
import json


if IS_PLONE_5:
    from plone.app.linkintegrity.utils import getIncomingLinks

    def isLinked(obj):
        # Important - Check all incoming references, not just tinymce relations
        for it in getIncomingLinks(obj=obj, intid=None, from_attribute=None):
            return True
        return False
else:
    from Products.CMFPlone.utils import isLinked


class DeleteBlocks(BrowserView):

    confirm_template = ViewPageTemplateFile(
        'templates/block_delete_confirmation.pt')

    def __init__(self, context, request):
        super(DeleteBlocks, self).__init__(context, request)
        self.block = None
        self.link_integrity = None

    def __call__(self):
        payload = self.request.get('data', None)
        if not payload:
            raise BadRequest('No data given')

        # TODO validate payload contains blocks and confirmed flag.
        if not IS_PLONE_5:
            from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo
            self.link_integrity = ILinkIntegrityInfo(self.request)

        data = json.loads(payload)
        self.block = uuidToObject(data['block'])

        if self.request.get('form.submitted', False):

            if self.link_integrity:
                # Always allow deletion of block, regardless of the integrity
                # check.
                self.request.environ[self.link_integrity.marker] = 'all'

            self.context.manage_delObjects([self.block.id])
            transaction_note('Deleted %s' % self.block.absolute_url())
            return json_response(self.request, proceed=True)
        else:
            return json_response(self.request,
                                 content=self.confirm_template(),
                                 proceed=False)

    def get_link_integrity_breaches(self):
        if isLinked(self.block):
            breaches_info = []

            if IS_PLONE_5:
                portal = api.portal.get()
                view = api.content.get_view(
                    'delete_confirmation_info',
                    portal,
                    self.request)
                sources = view.get_breaches([self.block, ])[0]['sources']
                for source in sources:
                    breaches_info.append({'title': source['title'],
                                          'url': source['url']})
            else:
                breaches = self.link_integrity.getIntegrityBreaches()
                sources = breaches.values()
                sources = len(sources) and sources[0] or sources

                for source in sources:
                    breaches_info.append({'title': source.title_or_id(),
                                          'url': source.absolute_url()})

            return breaches_info
        else:
            return None

    def is_locked_for_current_user(self):
        locking_info = self.block.restrictedTraverse('@@plone_lock_info', None)
        if locking_info:
            return locking_info.is_locked_for_current_user()
        else:
            return False

    @property
    def context_state(self):
        return self.block.restrictedTraverse('@@plone_context_state')

    def block_payload(self):
        block = IUUID(self.block)
        return json.dumps({'block': block})

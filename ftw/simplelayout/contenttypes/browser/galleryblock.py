from Acquisition._Acquisition import aq_inner
from ftw.simplelayout import _
from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone.app.imaging.utils import getAllowedSizes
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate


class GalleryBlockView(BaseBlock):
    """GalleryBlock default view"""

    template = ViewPageTemplateFile('templates/galleryblock.pt')

    def get_images(self):
        return self.context.listFolderContents(
            contentFilter=dict(portal_type=['Image']))

    def get_box_boundaries(self):
        return getAllowedSizes().get('simplelayout_galleryblock')

    @property
    def can_add(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission(
            'ftw.simplelayout: Add GalleryBlock', context)
        return bool(permission)

    def generate_image_alttext(self, img):
        title = img.title_or_id().decode('utf-8')
        return translate(_(u'image_link_alttext',
                           default=u'${title}, enlarged picture.',
                           mapping={'title': title}),
                         context=self.request)

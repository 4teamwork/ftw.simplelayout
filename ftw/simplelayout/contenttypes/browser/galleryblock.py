from Acquisition._Acquisition import aq_inner
from ftw.simplelayout import _
from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone.app.imaging.utils import getAllowedSizes
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


class GalleryBlockView(BaseBlock):
    """GalleryBlock default view"""

    template = ViewPageTemplateFile('templates/galleryblock.pt')

    def get_images(self):
        imgBrains = self.context.portal_catalog.searchResults(
            portal_type="Image",
            sort_on=self.context.sort_on,
            sort_order=self.context.sort_order,
            path='/'.join(self.context.getPhysicalPath()))
        images = []
        for img in imgBrains:
            images.append(img.getObject())
        return images

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
        title = safe_unicode(img.title_or_id())
        return translate(_(u'image_link_alttext',
                           default=u'${title}, enlarged picture.',
                           mapping={'title': title}),
                         context=self.request)

    def get_image_details(self, scale):
        return json.dumps({
            "url": scale.url,
            "width": scale.width,
            "height": scale.height,
        })

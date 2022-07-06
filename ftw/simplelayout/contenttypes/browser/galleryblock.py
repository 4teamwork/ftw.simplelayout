from Acquisition._Acquisition import aq_inner
from ftw.simplelayout import _
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.contenttypes.behaviors import IMediaFolderReference
from ftw.simplelayout.staging.interfaces import IStaging
from plone import api
from plone.app.imaging.scale import ImageScale
from plone.app.imaging.utils import getAllowedSizes
from plone.dexterity.utils import safe_utf8
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import os


class GalleryBlockView(BaseBlock):
    """GalleryBlock default view"""

    template = ViewPageTemplateFile('templates/galleryblock.pt')

    def has_mediafolder(self):
        if not IMediaFolderReference(self.context, None):
            return False
        return self.context.mediafolder and self.context.mediafolder.to_object

    def can_access_media_folder(self):
        if not self.has_mediafolder():
            return False
        return api.user.has_permission('View', obj=self.context.mediafolder.to_object)

    def get_images(self):

        if self.has_mediafolder() and self.can_access_media_folder():
            path = '/'.join(self.context.mediafolder.to_object.getPhysicalPath())
        else:
            # Edge case for migrations/updates
            path = '/'.join(self.context.getPhysicalPath())

        imgBrains = api.portal.get_tool('portal_catalog').searchResults(
            portal_type="Image",
            sort_on=self.context.sort_on,
            sort_order=safe_utf8(self.context.sort_order),
            path=path)
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

        types_tool = api.portal.get_tool('portal_types')
        addable_content = types_tool['ftw.simplelayout.GalleryBlock'].allowed_content_types
        return bool(permission) and len(addable_content)

    def can_add_mediafolder(self):
        context = aq_inner(self.context).aq_parent

        if IStaging(context, None) and IStaging(context).is_working_copy():
            context = IStaging(context).get_baseline()

        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission(
            'ftw.simplelayout: Add ContentPage', context)
        return bool(permission)

    def get_review_state_mediafolder(self):
        if self.has_mediafolder():
            wftool = api.portal.get_tool('portal_workflow')
            state_id = wftool.getInfoFor(
                self.context.mediafolder.to_object,
                'review_state',
                default=None)
            if state_id is None:
                return ''
            translated_state_title = translate(state_id, context=self.request, domain='plone')
            return u'<span class="state-{}">{}</span>'.format(
                state_id,
                translated_state_title
            )
        return ''

    def generate_image_alttext(self, img):
        title = safe_unicode(img.title_or_id())
        return translate(_(u'image_link_alttext',
                           default=u'${title}, enlarged picture.',
                           mapping={'title': title}),
                         context=self.request)

    def get_full_image_scale(self, img):
        scales = img.restrictedTraverse('@@images')
        try:
            scale = scales.scale('image', scale='sl_galleryblock_4k', direction='up')
        except IOError:
            scale = None

        if not scale:
            scale = self._get_fallback_image_scale()

        return scale.absolute_url()

    def get_image_scale_tag(self, img):
        scales = img.restrictedTraverse('@@images')
        try:
            scale = scales.scale('image', scale='simplelayout_galleryblock', direction='down')
        except IOError:
            scale = None

        if not scale:
            scale = self._get_fallback_image_scale()

        return u'<img src="{src}" height="{height}" width="{width}" alt="{alt}"/>'.format(
            src=scale.absolute_url(),
            height=scale.height,
            width=scale.width,
            alt=self.generate_image_alttext(img),
        )

    def _get_fallback_image_scale(self):
        current_folder = os.path.dirname(__file__)

        fallback_image_path = os.path.join(
            os.path.dirname(os.path.dirname(current_folder)),
            'browser',
            'resources',
            'image_unavailable.png'
        )

        with open(fallback_image_path, 'rb') as fallback_image:
            fallback_image_scale = FallbackImageScale(
                id='galleryblock_fallback_image',
                title='',
                data=fallback_image.read(),
                content_type='image/png',
            )

        return fallback_image_scale


class FallbackImageScale(ImageScale):
    def absolute_url(self):
        return api.portal.get().absolute_url() + '/++resource++ftw.simplelayout/image_unavailable.png'

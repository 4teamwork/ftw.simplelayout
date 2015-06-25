from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.interfaces import ISimplelayoutActions
from ftw.simplelayout.utils import normalize_portal_type
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


IMG_TAG_TEMPLATE = (
    '<div class="sl-image {cssClass}">'
    '<img src="{src}" alt="{alt}" />'
    '</div>')

IMG_TAG_TEMPLATE_WITH_LINK = (
    '<div class="sl-image {cssClass}">'
    '<a href="{teaser_url}" title={title}><img src="{src}" alt="{alt}" /></a>'
    '</div>')


class TextBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/textblock.pt')

    def teaser_url(self):
        teaser = ITeaser(self.context)
        if not teaser:
            return None

        if teaser.internal_link:
            return teaser.internal_link.to_object.absolute_url()
        elif teaser.external_link:
            return teaser.external_link
        else:
            return None

    def get_image(self):
        teaser_url = self.teaser_url()

        if self.context.image and not teaser_url:
            return IMG_TAG_TEMPLATE.format(
                **dict(
                    src=self._get_image_scale_url(),
                    cssClass='{0} {1}'.format(self._get_image_scale(),
                                              self._get_image_float()),
                    alt=self.context.Title()
                ))
        elif self.context.image and teaser_url:
            return IMG_TAG_TEMPLATE_WITH_LINK.format(
                **dict(
                    teaser_url = teaser_url,
                    title=self.context.Title(),
                    src=self._get_image_scale_url(),
                    cssClass='{0} {1}'.format(self._get_image_scale(),
                                              self._get_image_float()),
                    alt=self.context.Title()
                ))

        else:
            return None

    @memoize
    def _get_image_scale(self):
        scale = self.blockconfig.get('scale', '')
        if scale:
            return scale
        else:
            return self._get_default_scale()

    def _get_image_scale_url(self):
        scale = self._get_image_scale()
        scaler = self.context.restrictedTraverse('@@images')
        return scaler.scale('image', scale=scale).url

    @memoize
    def _get_default_actions(self):
        normalized_portal_type = normalize_portal_type(
            self.context.portal_type)

        actions = queryMultiAdapter(
            (self.context, self.request),
            ISimplelayoutActions,
            name='{0}-actions'.format(normalized_portal_type))
        return actions.specific_actions().items()[0][1]

    @memoize
    def _get_default_scale(self):
        return self._get_default_actions()['data-scale']

    @memoize
    def _get_image_float(self):
        image_float = self.blockconfig.get('imagefloat', '')

        if image_float:
            return image_float
        else:
            return self._get_default_image_float()

    @memoize
    def _get_default_image_float(self):
        return self._get_default_actions()['data-imagefloat']

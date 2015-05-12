from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutActions
from ftw.simplelayout.utils import normalize_portal_type
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


IMG_TAG_TEMPLATE = (
    '<div class="sl-image {cssClass}">'
    '<img src="{src}" alt="{alt}" />'
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

        if self.context.image:
            return IMG_TAG_TEMPLATE.format(
                **dict(
                    src=self._get_image_scale_url(),
                    cssClass=self._get_image_scale(),
                    alt=self.context.Title()
                ))
        else:
            return None

    @memoize
    def _get_image_scale(self):
        scale = IBlockConfiguration(self.context).load().get('scale', '')
        if scale:
            return IBlockConfiguration(self.context).load().get('scale', '')
        else:
            return self._get_default_scale()

    def _get_image_scale_url(self):
        scale = self._get_image_scale()
        scaler = self.context.restrictedTraverse('@@images')
        return scaler.scale('image', scale=scale).url

    @memoize
    def _get_default_scale(self):
        """Returns the first scale defined in textblock special actions"""
        normalized_portal_type = normalize_portal_type(
            self.context.portal_type)

        actions = queryMultiAdapter(
            (self.context, self.request),
            ISimplelayoutActions,
            name='{0}-actions'.format(normalized_portal_type))
        return actions.specific_actions().items()[0][1]['data-scale']
